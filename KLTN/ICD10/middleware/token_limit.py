import tiktoken
from django.http import JsonResponse
from ICD10.models.chatbot import ChatSession, ChatMessage
from google import genai
from django.conf import settings

# Cấu hình
MAX_TOKENS_PER_SESSION = 5000
SUMMARIZE_THRESHOLD = 4000

tokenizer = tiktoken.get_encoding("cl100k_base")


def count_tokens(text: str) -> int:
    if not text:
        return 0
    return len(tokenizer.encode(text))


def calculate_session_tokens(session_id):
    messages = ChatMessage.objects.filter(session_id=session_id).order_by("created_at")
    total = 0
    for m in messages:
        total += count_tokens(m.content)
    return total


def summarize_history(session_id):
    """Tóm tắt hội thoại khi token vượt ngưỡng."""

    msgs = ChatMessage.objects.filter(session_id=session_id).order_by("created_at")
    if not msgs.exists():
        return

    full_text = "\n".join([f"{m.role}: {m.content}" for m in msgs])

    prompt = f"""
    Hãy tóm tắt ngắn gọn hội thoại sau, giữ lại đầy đủ ngữ cảnh quan trọng:
    {full_text}
    """

    client = genai.Client(api_key=settings.GEMINI_API_KEY)

    res = client.models.generate_content(
        model="gemini-2.5-flash",
        contents=[{"parts": [{"text": prompt}]}],
    )
    summary = res.text.strip()

    # Reset session history
    ChatMessage.objects.filter(session_id=session_id).delete()
    ChatMessage.objects.create(
        session_id=session_id,
        role="system",
        content="[TÓM TẮT] " + summary
    )


class TokenLimitMiddleware:
    """
    Kiểm tra token mỗi session cho API chatbot trước khi xử lý request.
    """

    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):

        # Chỉ áp dụng cho API chat
        if request.path in ["/api/chat_with_ai"]:
            session_id = request.data.get("session_id")

            if session_id:
                session = ChatSession.objects.filter(id=session_id).first()

                if session:
                    total = calculate_session_tokens(session.id)

                    # Quá giới hạn -> trả lỗi
                    if total > MAX_TOKENS_PER_SESSION:
                        return JsonResponse({
                            "error": "Bạn đã dùng quá nhiều token cho cuộc hội thoại này. Vui lòng tạo cuộc trò chuyện mới."
                        }, status=429)

                    # Gần chạm limit -> tóm tắt
                    if total > SUMMARIZE_THRESHOLD:
                        summarize_history(session.id)

        # Cho phép request đi tiếp
        response = self.get_response(request)
        return response
