from django.conf import settings
from django.db import transaction
import time
from ICD10.models.chatbot import *
from ICD10.models.user import *
from ICD10.models.icd10 import *
from utils.utils import Utils
from libs.Redis import RedisWrapper
import google.generativeai as genai
import re
import json
import base64
import logging
import requests
from django.conf import settings
import numpy as np
from scipy.spatial.distance import cosine
from sentence_transformers import SentenceTransformer
import faiss
import google.generativeai as genai

# Cấu hình Google Generative AI API
genai.configure(api_key=settings.GEMINI_API_KEY)

logger = logging.getLogger(__name__)

class GeminiChatService:
    """Service để tương tác với Gemini API và quản lý chat"""
    
    def __init__(self):
        """Khởi tạo Gemini Chat Service"""
        
        # Dùng model embedding cục bộ
        self.model = SentenceTransformer("intfloat/multilingual-e5-base")
        self.faiss_index_path = "icd10_index_vi.faiss"
        self.texts_path = "icd10_texts_vi.npy"

        # Load FAISS index và danh sách bệnh
        logger.info("🔄 Loading FAISS index và ICD10 texts...")
        self.index = faiss.read_index(self.faiss_index_path)
        self.texts = np.load(self.texts_path, allow_pickle=True)
        
        # Cấu hình generation
        self.generation_config = {
            "temperature": 0.7,
            "top_p": 0.95,
            "top_k": 40,
            "max_output_tokens": 8192,
        }
        
        # Cấu hình an toàn
        self.safety_settings = [
            {
                "category": "HARM_CATEGORY_HARASSMENT",
                "threshold": "BLOCK_MEDIUM_AND_ABOVE"
            },
            {
                "category": "HARM_CATEGORY_HATE_SPEECH",
                "threshold": "BLOCK_MEDIUM_AND_ABOVE"
            },
            {
                "category": "HARM_CATEGORY_SEXUALLY_EXPLICIT",
                "threshold": "BLOCK_MEDIUM_AND_ABOVE"
            },
            {
                "category": "HARM_CATEGORY_DANGEROUS_CONTENT",
                "threshold": "BLOCK_MEDIUM_AND_ABOVE"
            },
        ]
        
        self.model_name = "gemini-2.5-flash"
    
        # Cache dữ liệu hệ thống để tái sử dụng
        self.system_data_cache = None
        self.cache_last_updated = None
        self.cache_ttl = 3600  # 1 giờ (thời gian tính bằng giây)
        
        
    # ==================================================================
    # CORE FUNCTIONS
    # ==================================================================

    def _call_gemini(self, prompt, retries=3, backoff=2) -> str:
        """Gọi API Gemini và trả về text"""
        try:
            url = f"https://generativelanguage.googleapis.com/v1beta/models/{self.model_name}:generateContent"
            headers = {"Content-Type": "application/json"}
            if isinstance(prompt, str):
                parts = [{"text": prompt}]
            else:
                parts = prompt  # Trường hợp parts là list (có inline_data image)
            payload = {
                "contents": [{"parts": parts}],
                "generationConfig": self.generation_config,
                "safetySettings": self.safety_settings,
            }

            for attempt in range(retries):
                res = requests.post(
                    f"{url}?key={settings.GEMINI_API_KEY}",
                    headers=headers,
                    json=payload,
                    timeout=60
                )
                # Nếu thành công
                if res.status_code == 200:
                    data = res.json()
                    return data["candidates"][0]["content"]["parts"][0]["text"]

                # Nếu bị 429 Too Many Requests → chờ backoff
                elif res.status_code == 429:
                    wait_time = backoff ** attempt
                    logger.warning(f"Gemini rate limited. Waiting {wait_time}s before retry...")
                    time.sleep(wait_time)
                    continue

                # Nếu lỗi khác → raise
                else:
                    res.raise_for_status()

            logger.error("Gemini API exhausted retries after multiple attempts.")
            return "Xin lỗi, hiện tại hệ thống AI đang quá tải, vui lòng thử lại sau."

        except Exception as e:
            logger.error(f"Lỗi gọi Gemini API: {e}")
            return "Xin lỗi, hiện tại tôi không thể kết nối đến hệ thống AI."
    
    # ==================================================================
    # INTENT DETECTION
    # ==================================================================

    def detect_intent(self, user_input: str, last_bot_message: str = "") -> str:
        """
        Nhận diện loại yêu cầu của người dùng — hybrid rule + Gemini.
        """
        text = user_input.lower().strip()
        
        # 1️⃣ Phát hiện hội thoại xã giao (CHAT_GENERAL)
        if re.search(r"\b(bạn là ai|bạn tên gì|ai tạo ra bạn|cảm ơn|hello|xin chào|hi|thanks|tạm biệt)\b", text):
            return "CHAT_GENERAL"

        # 1️⃣ Luật thủ công nhanh
        if re.search(r"\b(tôi bị|triệu chứng|mắc bệnh|bệnh gì|đau|ngứa|ho|sốt|chóng mặt|mệt)\b", text):
            return "SYMPTOM_PREDICT"

        if re.search(r"\b(icd10|mã bệnh|tra mã|tra cứu icd|mã icd10|mã|bệnh|thông tin|thông tin bệnh|)\b", text) or re.search(r"\b[A-Z]\d{2}(\.\d+)?\b", text):
            return "DISEASE_INFO"

        # if re.search(r"\b[A-Z]\d{2}(\.\d+)?\b", user_input):
        #     return "DISEASE_INFO"
        
        if last_bot_message:
        # Nếu người dùng nhắc lại tên bệnh trong câu trước
            last_diseases = re.findall(r"[A-Z]\d{2}(\.\d+)?|[A-Z][a-z]+", last_bot_message)
            for disease_name in last_diseases:
                if disease_name.lower() in text:
                    return "FOLLOW_UP"
                
        # ✅ 1️⃣ Kiểm tra cache trước
        cache_key = f"intent_{hash(user_input)}"
        cached_intent = RedisWrapper.get(cache_key)
        if cached_intent:
            logger.debug(f"✅ Dùng intent từ Redis cache: {cached_intent}")
            return cached_intent

        # 2️⃣ Nếu không khớp, fallback sang Gemini để phân loại
        intent_prompt = (
            "Phân loại câu hỏi sau vào 1 trong các nhóm sau:\n"
            "- ICD10_SEARCH: nếu hỏi về bệnh, mã ICD10 hoặc chẩn đoán.\n"
            "- SYMPTOM_PREDICT: nếu mô tả triệu chứng hoặc hỏi 'tôi bị ...' hay 'bệnh gì'.\n"
            "- DISEASE_INFO: nếu hỏi chi tiết về một mã bệnh cụ thể (ví dụ: L20.9).\n"
            "- FOLLOW_UP: nếu hỏi tiếp thông tin về bệnh vừa được đề cập trước đó.\n"
            "- CHAT_GENERAL: nếu là câu hỏi xã giao hoặc không liên quan y tế.\n"
            "- GENERAL: nếu là câu hỏi thông thường hoặc xã giao.\n\n"
            f"Câu hỏi: \"{user_input}\"\n"
            "Trả về JSON {\"intent\": \"...\"} duy nhất, không thêm gì khác."
        )

        result = self._call_gemini(intent_prompt)
        try:
            intent_data = json.loads(result)
            intent = intent_data.get("intent", "GENERAL").upper()

            # ✅ 3️⃣ Lưu lại cache trong 10 phút
            RedisWrapper.save(cache_key, intent, expire_time=600)
            logger.debug(f"💾 Cache intent mới: {intent}")

            return intent
        except Exception:
            return "GENERAL"
        

    # ==================================================================
    # ICD10 SEARCH
    # ==================================================================
        
    def search_icd10(self, query):
        """Gọi AI để tìm bệnh ICD10 có liên quan, có Redis cache và tự refresh mỗi giờ."""
        # ✅ 1️⃣ Chuẩn hóa query
        if isinstance(query, (list, tuple)):
            query_str = ", ".join(map(str, query))
        else:
            query_str = str(query)

        if not query_str.strip():
            logger.warning("Empty query passed to search_icd10.")
            return []

        # 1️⃣ Sinh embedding cho câu hỏi bằng local model
        logger.info("🧠 Đang sinh embedding cho câu hỏi...")
        query_emb = self.model.encode([f"query: {query_str}"], normalize_embeddings=True)
        
        top_k = 30
        # 2️⃣ Tìm top-k bệnh gần nhất trong FAISS
        logger.info("🔍 Đang tìm top bệnh liên quan...")
        scores, indices = self.index.search(np.array(query_emb, dtype=np.float32), top_k)
        top_texts = [self.texts[i] for i in indices[0]]
        
        # 3️⃣ Tạo ngữ cảnh cho Gemini reasoning
        context = "\n".join(top_texts)

        # ✅ 3️⃣ Tạo prompt cho Gemini
        prompt = (
            Constants.PROMPT_AI_SEARCH
            .replace("{query}", query_str)
            .replace("{context}", context)
            .replace("{top_k}", str(top_k))
        )

        # ✅ 4️⃣ Gọi Gemini và parse kết quả
        try:
            text_output = self._call_gemini(prompt)
            return json.loads(text_output)
        except json.JSONDecodeError:
            logger.error(f"Gemini trả về kết quả không phải JSON: {text_output}")
            return []
        except Exception as e:
            logger.error(f"Lỗi khi parse kết quả tìm kiếm ICD10: {e}")
            return []
        
        
    # ==================================================================
    # PRECISE DISEASE
    # ==================================================================

    def predict_disease(self, user, text_query, image_file=None, session_id=None, request=None):
        """Phân tích triệu chứng (văn bản + ảnh), trả về danh sách bệnh ICD10."""

        # 2️⃣ Lấy hoặc tạo session
        session = (
            ChatSession.objects.filter(id=session_id).first()
            if session_id
            else ChatSession.objects.create(user=user)
        )

        # 3️⃣ Nếu có ảnh, upload S3
        image_base64 = None
        mime_type = None

        if image_file:
            image_bytes = image_file.read()   # đọc trước
            mime_type = image_file.content_type
            image_base64 = base64.b64encode(image_bytes).decode("utf-8")
        

        # 5️⃣ Cache kiểm tra
        cache_key = f"ai_predict_{hash(text_query)}"
        cached_result = RedisWrapper.get(cache_key)
        if cached_result:
            logger.info("Using cached AI prediction result.")
            return cached_result

        # 6️⃣ Chuẩn bị prompt
        parts = []
        if image_file and text_query:
            prompt_text = Constants.PROMPT_AI_IMAGE.replace("{text_query}", text_query)
            parts.append({"text": prompt_text})
            parts.append({
                "inline_data": {"mime_type": mime_type, "data": image_base64}
            })
        else:
            prompt_text = Constants.PROMPT_AI_TEXT.replace("{text_query}", text_query)
            parts.append({"text": prompt_text})

        # 7️⃣ Gọi Gemini
        text_output = self._call_gemini(parts)
        try:
            keywords = json.loads(text_output)
        except Exception:
            logger.warning("Gemini returned non-JSON response, fallback empty list.")
            keywords = []

        print(f"Extracted keywords: {keywords}")
        # Search ICD10
        diseases = self.search_icd10(keywords)

    
        # 🔟 Lưu cache
        result = {"session_id": session.id, "keywords": keywords, "diseases": diseases}
        RedisWrapper.save(cache_key, result, 3600)

        # Kiểm tra tóm tắt
        total_msgs = ChatMessage.objects.filter(session=session).count()
        if total_msgs >= (session.summary_count + 1) * 20:
            self.summarize_conversation(session.id)
            session.summary_count += 1
            session.save()

        return result


    # ==================================================================
    # DISEASE INFO
    # ==================================================================

    def get_disease_info(self, code: str):
        """Trả về thông tin chi tiết bệnh theo mã ICD10"""
        try:
            disease = ICDDisease.objects.filter(code__iexact=code).first()
            disease_extra = DiseaseExtraInfo.objects.filter(disease=disease).first()
            if not disease:
                return f"Không tìm thấy bệnh với mã ICD10: {code}"

            return (
                f"**{disease.code} – {disease.title_vi}**\n\n"
                f"Mô tả: {disease_extra.description or 'Chưa có mô tả.'}\n\n"
                f"Triệu chứng: {disease_extra.symptoms or 'Chưa có thông tin triệu chứng.'}\n\n"
                f"Ảnh minh họa: {disease_extra.image_url or 'Chưa có ảnh minh họa.'}\n\n"
                f"Xem chi tiết tại: http://127.0.0.1:8000/api/disease/{disease.code}"
            )
        except Exception as e:
            logger.error(f"Lỗi khi lấy thông tin bệnh: {e}")
            return "Không thể truy xuất dữ liệu bệnh từ hệ thống."

    # ==================================================================
    # CHAT FLOW
    # ==================================================================
    def _process_query(self, message_content, user, image_file=None):
        """Xác định intent và xử lý theo loại"""
        intent = self.detect_intent(message_content)
        logger.info(f"Intent: {intent}")

        if intent == "SYMPTOM_PREDICT":
            data = self.predict_disease(user, message_content, image_file=image_file)
            if isinstance(data, tuple):
                data = data[0]  # fallback để tránh crash
            return {
                "content": json.dumps(data.get("diseases", []), ensure_ascii=False),
                "source_type": "AI_PREDICT"
            }

        elif intent == "DISEASE_INFO":
            match = re.search(r"[A-Z]\d{2}(\.\d+)?", message_content)
            if match:
                info = self.get_disease_info(match.group(0))
                return {"content": info, "source_type": "DB"}
            else:
                return {"content": "Vui lòng cung cấp mã ICD10 để tra cứu.", "source_type": "BOT"}

        elif intent == "ICD10_SEARCH":
            results = self.search_icd10(message_content)
            if results:
                return {"content": json.dumps(results, ensure_ascii=False), "source_type": "AI_SEARCH"}
            return {"content": "Không tìm thấy kết quả phù hợp trong ICD10.", "source_type": "BOT"}

        else:  # GENERAL
            reply = self._call_gemini(f"Người dùng hỏi: {message_content}")
            return {"content": reply, "source_type": "AI_GENERAL"}

    
    # ==================================================================
    # SUMMARY MANAGEMENT
    # ==================================================================

    def summarize_conversation(self, session_id: int):
        """Tóm tắt hội thoại và lưu Redis"""
        messages = ChatMessage.objects.filter(session_id=session_id).order_by("created_at")
        combined = "\n".join([f"{m.role}: {m.content}" for m in messages])

        summary_prompt = (
            f"Tóm tắt ngắn gọn hội thoại sau bằng 5 dòng, "
            f"giữ lại tên bệnh và hành động quan trọng:\n{combined}"
        )
        summary = self._call_gemini(summary_prompt)
        RedisWrapper.save(f"summary:{session_id}", summary, expire_time=86400)
        logger.info(f"Saved summary for session {session_id}")
        return summary
    
    @transaction.atomic
    def create_chat_session(self, user):
        """Tạo phiên chat mới cho người dùng"""
        try:
            # Tạo phiên chat mới
            session = ChatSession.objects.create(
                user=user,
                title="Phiên chat mới"
            )
            
            # Trả về phiên chat
            return session
            
        except Exception as e:
            self.logger.error(f"Lỗi khi tạo phiên chat: {str(e)}")
            raise e
    
    @transaction.atomic
    def send_message(self, user, message_content, session_id=None):
        """Gửi tin nhắn và lưu vào cơ sở dữ liệu"""
        try:
            # Tìm hoặc tạo phiên chat
            if session_id:
                try:
                    chat_session = ChatSession.objects.get(id=session_id, user=user)
                except ChatSession.DoesNotExist:
                    chat_session = self.create_chat_session(user)
            else:
                # Tìm phiên chat gần nhất chưa kết thúc của user
                chat_session = ChatSession.objects.filter(
                    user=user,
                    is_ended=False
                ).order_by('-created_at').first()
                
                if not chat_session:
                    chat_session = self.create_chat_session(user)
                
            # Lưu tin nhắn của người dùng
            user_message = ChatMessage.objects.create(
                session=chat_session,
                role="user",
                content=message_content
            )
            
            # Phân tích và xử lý yêu cầu để xác định nguồn dữ liệu
            response_data = self._process_query(message_content, user)
            
            # Lưu phản hồi của AI
            ai_message = ChatMessage.objects.create(
                session=chat_session,
                role="bot",
                content=response_data["content"]
            )
            
            # Format timestamp theo định dạng Việt Nam
            def format_timestamp(timestamp):
                if not timestamp:
                    return "Không có thời gian"
                try:
                    return timestamp.strftime("%d/%m/%Y %H:%M:%S")
                except Exception:
                    return "Invalid Date"
            
            # Cập nhật tiêu đề phiên chat nếu cần
            if chat_session.title == "Phiên chat mới" and len(message_content) > 10:
                try:
                    # Sử dụng Gemini API để tạo tiêu đề thông minh
                    title = self.generate_chat_title(message_content)
                    chat_session.title = title
                    chat_session.save()
                except Exception as e:
                    self.logger.error(f"Lỗi khi tạo tiêu đề thông minh: {str(e)}")
                    # Fallback to simple title creation
                    if len(message_content) <= 50:
                        title = message_content
                    else:
                        words = message_content.split()
                        if len(words) <= 8:
                            title = message_content[:50] + '...' 
                        else:
                            title = ' '.join(words[:8]) + '...'
                            
                    chat_session.title = title
                    chat_session.save()
            
            # Trả về thông tin tin nhắn và phiên chat
            return {
                "session_id": chat_session.id,
                "title": chat_session.title,
                "user_message": {
                    "id": str(user_message.id),
                    "content": user_message.content,
                    "timestamp": format_timestamp(user_message.timestamp)
                },
                "bot_message": {
                    "id": str(ai_message.id),
                    "content": ai_message.content,
                    "source_type": response_data["source_type"],
                    "timestamp": format_timestamp(ai_message.timestamp)
                }
            }
            
        except Exception as e:
            self.logger.error(f"Lỗi khi gửi tin nhắn: {str(e)}")
            return {
                "error": f"Đã xảy ra lỗi: {str(e)}"
            }
    

    def generate_chat_title(self, message_content):
        """Tạo tiêu đề thông minh cho phiên chat dựa trên nội dung tin nhắn đầu tiên"""
        try:
            # Khởi tạo model
            model = self._initialize_generative_model()
            
            # Tạo prompt để sinh tiêu đề
            prompt = f"""Tin nhắn: "{message_content}"
            
            Hãy tạo một tiêu đề ngắn gọn (dưới 50 ký tự) cho cuộc trò chuyện này.
            Chỉ trả về tiêu đề, không có giải thích hay định dạng thêm.
            Tiêu đề phải bằng tiếng Việt và mô tả ngắn gọn nội dung chính của tin nhắn.
            """
            
            # Gọi API với cấu hình temperature thấp hơn để có kết quả ổn định
            title_config = self.generation_config.copy()
            title_config["temperature"] = 0.1
            title_config["max_output_tokens"] = 50
            
            response = model.generate_content(
                prompt,
                generation_config=title_config,
                safety_settings=self.safety_settings
            )
            
            # Làm sạch tiêu đề
            title = response.text.strip().replace('"', '').replace('\n', ' ')
            
            # Giới hạn độ dài tiêu đề
            if len(title) > 50:
                title = title[:47] + '...'
            
            return title
            
        except Exception as e:
            self.logger.error(f"Lỗi khi tạo tiêu đề thông minh: {str(e)}")
            # Fallback to simple title creation
            if len(message_content) <= 50:
                return message_content
            else:
                words = message_content.split()
                if len(words) <= 8:
                    return message_content[:50] + '...'
                else:
                    return ' '.join(words[:8]) + '...' 

    def _get_icd10_context(self, limit=300):
        """Tạo danh sách code và title để đưa vào prompt."""
        diseases = ICDDisease.objects.all().values("code", "title_vi")[:limit]
        disease_lines = [f"{d['code']} - {d['title_vi']}" for d in diseases]
        return "\n".join(disease_lines)
