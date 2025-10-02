class Constants:
    USER_STATUS = (
        (1, "Active"),
        (2, "Inactive"),
        (3, "Waiting"),
    )
    ROLE = (
        (1, "GUEST"),
        (2, "DOCTOR"),
        (3, "ADMIN")
    )
    
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
    
    PRODUCT_STATUS = [
        ('in_stock', 'In Stock'),
        ('out_of_stock', 'Out Of Stock'),
    ]


    CHANGE_PASSWORD = "CHANGE_PASSWORD"
    ADMIN_REGISTER_USER = "ADMIN_REGISTER_USER"
    USER_CREATE_NEWS = "USER_CREATE_NEWS"
    USER_UPDATE_NEWS = "USER_UPDATE_NEWS"
    USER_DELETE_NEWS = "USER_DELETE_NEWS"
    USER_UPDATE_NEWS_CATEGORY = "USER_UPDATE_NEWS_CATEGORY"
    USER_CREATE_NEWS_CATEGORY = "USER_CREATE_NEWS_CATEGORY"
    USER_DELETE_NEWS_CATEGORY = "USER_DELETE_NEWS_CATEGORY"
    USER_UPDATE_PRODUCT_CATEGORY = "USER_UPDATE_PRODUCT_CATEGORY"
    USER_CREATE_FEEDBACK = "USER_CREATE_FEEDBACK"
    USER_UPDATE_FEEDBACK = "USER_UPDATE_FEEDBACK"
    USER_DELETE_FEEDBACK = "USER_DELETE_FEEDBACK"
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
    CACHE_KEY_DISEASES_CHILDREN = "icd10_subdiseases"
    