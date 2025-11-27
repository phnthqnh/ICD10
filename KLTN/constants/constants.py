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
    
    # ICD10
    CACHE_KEY_DISEASES_BY_CODE = "CACHE_KEY_DISEASES_BY_CODE_{}"  # Thêm định dạng cho mã bệnh
    
    # Notification
    NOTIFICATION_TYPE_CHOICES = (
        ('feedback', 'Feedback'),
        ('verify', 'Doctor Verification'),
        ('system', 'System'),
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
        "Bạn là một chuyên gia y tế. Chuyên gia về QUẢN LÝ MÃ HOÁ LÂM SÀNG KHÁM CHỮA BỆNH ICD10. "
        "Đây là mảng các triệu chứng: [{query}].\n\n"
        "Dưới đây là danh sách {top_k} bệnh ICD10 có thể liên quan:\n{context}\n\n"
        "Hãy trả về một JSON các mã bệnh trong ICD10 có liên quan đến các triệu chứng tôi cung cấp, với độ liên quan >= 90%. "
        "Mỗi bệnh phải trả về một cách chính xác tuyệt đối trong danh sách các bệnh ở ICD10, trả về dạng JSON: {{\"code\": \"Mã ICD10\", \"title\": \"Tên bệnh\", \"score\": \"độ liên quan (0-100%)\"}}. "
        "Chỉ trả JSON, không thêm mô tả nào khác. "
        "TUYỆT ĐỐI KHÔNG được bọc JSON trong ```json hoặc bất kỳ định dạng markdown nào khác. Phản hồi của bạn phải bắt đầu bằng ký tự '[' và kết thúc bằng ký tự ']'."
    )
    
    PROMPT_AI_SUMMARY = (
        "Hãy đọc toàn bộ đoạn hội thoại dưới đây giữa bệnh nhân và chatbot y tế, "
        "và tóm tắt nội dung chính (triệu chứng, chẩn đoán, bệnh liên quan) "
        "bằng tiếng Việt, súc tích (dưới 200 từ):\n\n {full_text}"
    )