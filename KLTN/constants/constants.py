class Constants:
    USER_STATUS = (
        (1, "Active"),
        (2, "Inactive"),
        (3, "Waiting"),
    )
    FEEDBACK_TYPE = (
        (1, "Chapter"),
        (2, "Block"),
        (3, "Disease"),
    )
    FEEDBACK_STATUS = (
        (1, "Accepted"),
        (2, "Rejected"),
        (3, "Pending"),
    )
    ROLE = (
        (1, "GUEST"),
        (2, "DOCTOR"),
        (3, "ADMIN")
    )
    
    ROLE_CHAT = [
        ("user", "User"),
        ("bot", "Chatbot"),
        ("admin", "Admin"),
    ]
    
    DATA_TYPES = [
        ("char", "Text"),
        ("varchar", "Variable Character"),
        ("integer", "Integer"),
        ("bigint", "Big Integer"),
        ("smallint", "Small Integer"),
        ("float", "Float"),
        ("double", "Double Precision Float"),
        ("decimal", "Decimal"),
        ("numeric", "Numeric"),
        ("boolean", "Boolean"),
        ("datetime", "DateTime"),
        ("timestamp", "Timestamp"),
        ("enum", "Enum"),
        ("array", "Array"),
    ]

    RELATION_TYPES = [
        ("foreignkey", "Foreign Key"),
        ("manytoone", "Many-to-One"),
        ("onetoone", "One-to-One"),
        ("manytomany", "Many-to-Many"),
        ("social_media", "Social-Media"),
    ]


    CHANGE_PASSWORD = "CHANGE_PASSWORD"
    ADMIN_REGISTER_USER = "ADMIN_REGISTER_USER"
    USER_REGISTER = "USER_REGISTER"
    REGISTER = "REGISTER"
    EDIT_USER_PROFILE = "EDIT_USER_PROFILE"
    EMAIL_DEFAULT_TEMPLATE_ADMIN_REGISTER_USER = "Default Admin Register User Template"
    EMAIL_DEFAULT_FORGOT_PASSWORD_TEMPLATE = "Default Forgot Password Template"
    CHANGE_PASSWORD_TIME = 1800
    ATTEMPT_BLOCK_USER = 1800
    ADMIN_REGISTER_USER_TIME = 259200
    ALLOWED_EXTENSIONS = [".pdf", ".docx", ".doc", ".xlsx", ".xls"]
    MAX_FILE_SIZE_MB = 20
    ALLOWED_AVATAR_TYPES = ["image/jpeg", "image/png", "image/gif", "image/bmp", "image/tiff", "image/webp"]
    ALLOWED_FILE_EXTENSIONS = ["pdf", "doc", "docx", "xls", "xlsx", "txt", "zip", "rar"]
    MAX_AVATAR_SIZE_MB = 5
    JWT_EXPIRATION = 1800
    
    # Redis
    CACHE_KEY_WAITING_USERS = "users_waiting_verification"
    CACHE_KEY_CHAPTERS = "icd10_chapters"
    CACHE_KEY_BLOCKS = "icd10_blocks"
    CACHE_KEY_DISEASES = "icd10_diseases"
    CACHE_KEY_DISEASES_CODE = "icd10_disease_code"
    CACHE_KEY_DISEASES_CHILDREN = "icd10_subdiseases"
    CACHE_DATA_CHAPTER = "icd10_data_chapter"
    CACHE_DATA_BLOCK = "icd10_data_block"
    CACHE_DATA_DISEASE = "icd10_data_disease"
    CACHE_EMAIL = "user_email"
    CACHE_USER_SESSION = "user_session"
    CACHE_MESSAGE_SESSION = "message_session"
    
    # ICD10
    CACHE_KEY_DISEASES_BY_CODE = "CACHE_KEY_DISEASES_BY_CODE_{}"  # Thêm định dạng cho mã bệnh
    
    # Notification
    NOTIFICATION_TYPE_CHOICES = (
        ('feedback', 'Feedback'),
        ('verify', 'Doctor Verification'),
        ('system', 'System'),
        ('admin_feedback_icd', 'Admin Feedback ICD'),
        ('admin_feedback_chatbot', 'Admin Feedback Chatbot'),
        ('admin_doctor', 'Admin Doctor Verification'),
    )
    
    # Gemini API
    GEMINI_API_URL = "https://generativelanguage.googleapis.com/v1beta/models/gemini-2.5-pro:generateContent"
    REQUEST_TIMEOUT = 180 # (giây)
    
    # Prompt template
    PROMPT_AI_IMAGE = (
        "Bạn là một chuyên gia y tế."
        "Hãy phân tích hình ảnh vùng da dưới đây và câu hỏi [{text_query}]. "
        "Hãy trả về danh sách các từ khóa liên quan đến bệnh lý có thể gặp, ở dạng JSON, ví dụ: [\"viêm da\", \"eczema\", \"hắc lào\"]."
        "Chỉ nên đưa các key y học có ý nghĩa như: 'nấm da', 'viêm da', 'eczema', 'hắc lào', ..."
        "TUYỆT ĐỐI KHÔNG được bọc JSON trong ```json hoặc bất kỳ định dạng markdown nào khác. Phản hồi của bạn phải bắt đầu bằng ký tự '[' và kết thúc bằng ký tự ']'."
    )
    
    PROMPT_AI_TEXT = (
        "Bạn là một chuyên gia y tế."
        "Bệnh nhân mô tả tình trạng sức khỏe như sau: [{text_query}]. "
        "Hãy trả về danh sách các từ khóa liên quan đến bệnh lý có thể gặp, ở dạng JSON, ví dụ: [\"viêm da\", \"eczema\", \"hắc lào\"]."
        "Chỉ nên đưa các key y học có ý nghĩa như: 'nấm da', 'viêm da', 'eczema', 'hắc lào', ..."
        "TUYỆT ĐỐI KHÔNG được bọc JSON trong ```json hoặc bất kỳ định dạng markdown nào khác. Phản hồi của bạn phải bắt đầu bằng ký tự '[' và kết thúc bằng ký tự ']'."
    )
    
    # PROMPT_AI_SEARCH = (
    #     "Bạn là một chuyên gia y tế. Chuyên gia về QUẢN LÝ MÃ HOÁ LÂM SÀNG KHÁM CHỮA BỆNH ICD10. "
    #     "Dưới đây là danh sách bệnh hiện có trong hệ thống:\n"
    #     "{icd10_context}\n\n"
    #     "Đây là mảng các triệu chứng: [{query}]. "
    #     "Hãy trả về một JSON các mã bệnh trong ICD10 có liên quan đến các triệu chứng tôi cung cấp, với độ liên quan >= 90%. "
    #     "Mỗi bệnh phải trả về một cách chính xác tuyệt đối trong danh sách các bệnh ở ICD10, trả về dạng JSON: {{\"code\": \"Mã ICD10\", \"title\": \"Tên bệnh\", \"score\": \"độ liên quan (0-100%)\"}}. "
    #     "Chỉ trả JSON, không thêm mô tả nào khác. "
    #     "TUYỆT ĐỐI KHÔNG được bọc JSON trong ```json hoặc bất kỳ định dạng markdown nào khác. Phản hồi của bạn phải bắt đầu bằng ký tự '[' và kết thúc bằng ký tự ']'."
    # )
    
    PROMPT_AI_SEARCH = (
        "Bạn là chuyên gia y tế, chuyên sâu về MÃ HÓA LÂM SÀNG ICD-10.\n\n"
        "Triệu chứng người dùng nhập: {query}\n\n"
        "Dưới đây là danh sách {top_k} bệnh gần nhất theo embedding:\n"
        "{context}\n\n"
        "Nhiệm vụ của bạn:\n"
        "1. Phân tích mức độ liên quan giữa triệu chứng và các bệnh ICD-10.\n"
        "2. Chỉ chọn ra những bệnh có mức độ phù hợp CAO (tương đương ≥ 90%).\n"
        "3. Hãy trả về JSON THUẦN không markdown với danh sách các phần tử dạng:\n"
        "   {\"code\": \"Mã ICD10\", \"title\": \"Tên bệnh\", \"score\": 0-100}\n"
        "4. JSON phải bắt đầu bằng '[' và kết thúc bằng ']'.\n"
        "5. Tuyệt đối không được thêm bất kỳ mô tả nào bên ngoài JSON.\n"
    )
    
    PROMPT_AI_SUMMARY = (
        "Hãy đọc toàn bộ đoạn hội thoại dưới đây giữa bệnh nhân và chatbot y tế, "
        "và tóm tắt nội dung chính (triệu chứng, chẩn đoán, bệnh liên quan) "
        "bằng tiếng Việt, súc tích (dưới 200 từ):\n\n {full_text}"
    )
    
    PROMPT_AI_INFO = (
        "Bạn là một chuyên gia y tế.\n"
        "Người dùng muốn bạn cung cấp thông tin về mã bệnh {context}\n"
        "Hãy trả về cho người dùng 3-4 câu đặc thù liên quan nhất đến mã bệnh, cơ bản bằng tiếng Việt, súc tích.\n"
        "Không nên dùng thuật ngữ quá mức y tế vì người dùng có thể là bệnh nhân.\n"
        "**Nguyên tắc tương tác:**\n\n"

        "* **Giọng điệu:** Chuyên nghiệp, chính xác và hữu ích.\n"
        "* **Rõ ràng:** Khi cung cấp mã từ tìm kiếm, hãy luôn bao gồm mô tả chính thức của mã đó.\n"
        "* **Mơ hồ:** Nếu truy vấn tìm kiếm của người dùng không rõ ràng (ví dụ: \"tiểu đường\"), đừng chỉ trả về kết quả đầu tiên. Hãy đặt những câu hỏi làm rõ để thu hẹp phạm vi tìm kiếm (ví dụ: \"Bạn đang tìm kiếm tiểu đường tuýp 1, tuýp 2 hay tiểu đường thai kỳ?\").\n"
        "* **Chủ động:** Nếu tìm kiếm trả về nhiều mã khả thi, hãy đưa ra 2-3 tùy chọn có khả năng xảy ra nhất và đề nghị tinh chỉnh tìm kiếm.\n"
        
    )