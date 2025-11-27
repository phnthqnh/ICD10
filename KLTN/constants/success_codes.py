class SuccessCodes:
    # Default
    DEFAULT = (0, "")
    
    # User
    LOGIN = ("AU_S_001", "Login successfully!")
    GET_USER = ("GET_USER", "Get user successfully!")
    USER_INFOR = ("USER_INFOR", "User infor")
    GET_USER = ("GET_USER", "Get user successfully!")
    LOGOUT = ("AU_S_002", "Loogut successfully!")
    REGISTER = ("AU_S_003", "Register successfully!")
    RESEND_VERIFICATION = ("RESEND_VERIFICATION", "Resend verification successfully!")
    ADMIN_CREATE_USER = ("CREATE_USER", "Register user successfully!")
    UPDATE_USER_PROFILE = ("UPDATE_USER_PROFILE", "Update User profile successfully!")
    LIST_USER = ("LIST_USER", "users")
    CREATE_USER = ("CREATE_USER", "User create successfully!")
    UPDATE_USER = ("UPDATE_USER", "User update successfully!")
    UPLOAD_AVATAR = ("UPLOAD_AVATAR", "Upload avatar successfully!")
    DELETE_USER = ("DELETE_USER", "User delete successfully!")
    CHANGE_PASSWORD = ("CHANGE_PASSWORD", "Change Password successfully!")
    ADMIN_INFOR = ("ADMIN_INFOR", "admin_infor")
    VERIFIED_DOCTOR = ("VERIFIED_DOCTOR", "User verified doctor successfully!")
    PASSWORD_RESET_EMAIL_SENT = ("PASSWORD_RESET_EMAIL_SENT", "Password reset email sent successfully!")
    PASSWORD_RESET_SUCCESS = ("PASSWORD_RESET_SUCCESS", "Password has been reset successfully!")
    GET_USER_PROFILE = ("GET_USER_PROFILE", "Get user profile successfully!")
    
    # Admin
    LIST_VERIFICATION = ("LIST_VERIFICATION", "List users waiting for verification successfully!")

    # token
    REFRESH_TOKEN = ("AU_S_003", "Token refreshed successfully")

    # Permission
    ASSIGN_PERMISSION = ("AU_S_004", "Permission assigned successfully")
    LIST_PERMISSION = ("LIST_PERMISSION", "Permissions")
    CREATE_PERMISSION = ("CREATE_PERMISSION", "Permission create successfully!")
    UPDATE_PERMISSION = ("UPDATE_PERMISSION", "Permission update successfully!")
    DELETE_PERMISSION = ("DELETE_PERMISSION", "Permission delete successfully!")

    # Group
    LIST_GROUP = ("LIST_GROUP", "groups")
    CREATE_GROUP = ("CREATE_GROUP", "Group create successfully!")
    UPDATE_GROUP = ("UPDATE_GROUP", "Group update successfully!")
    DELETE_GROUP = ("DELETE_GROUP", "Group delete successfully!")

    # EMail
    SEND_EMAIL_CHANGE_PASSWORD = (
        "SEND_EMAIL_CHANGE_PASSWORD",
        "Successfully send email!",
    )
    SEND_EMAIL_REGISTER_USER = (
        "SEND_EMAIL_REGISTER_USER",
        "Send email register to user successfully!",
    )
    RE_SEND_EMAIL_REGISTER_USER = (
        "RE_SEND_EMAIL_REGISTER_USER",
        "Re send email register to user!",
    )
    
    # ICD10
    GET_CHAPTERS = (
        "GET_CHAPTERS",
        "Get ICD-10 chapters successfully!",
    )
    
    GET_BLOCKS_BY_CHAPTER = (
        "GET_BLOCKS_BY_CHAPTER",
        "Get ICD-10 blocks by chapter successfully!",
    )
    
    GET_DISEASES_BY_BLOCK = (
        "GET_DISEASES_BY_BLOCK",
        "Get ICD-10 diseases by block successfully!",
    )
    
    GET_DISEASES_CHILDREN = (
        "GET_DISEASES_CHILDREN",
        "Get ICD-10 diseases children successfully!",
    )
    
    GET_DISEASE_CODE = (
        "GET_DISEASE_CODE",
        "Get ICD-10 diseases successfully!",
    )
    
    GET_DISEASE_BY_CODE = (
        "GET_DISEASE_BY_CODE",
        "Get ICD-10 disease by code successfully!",
    )
    
    SEARCH_DISEASES = (
        "SEARCH_DISEASES",
        "Search ICD-10 diseases successfully!",
    )
    
    GET_DATA_CHAPTER = (
        "GET_DATA_CHAPTER",
        "Get ICD-10 data chapter successfully!",
    )
    
    GET_DATA_BLOCK = (
        "GET_DATA_BLOCK",
        "Get ICD-10 data block successfully!",
    )
    
    GET_DATA_DISEASE = (
        "GET_DATA_DISEASE",
        "Get ICD-10 data disease successfully!",
    )
    
    #FEEDBACKS
    GET_FEEDBACKS_ICD10 = (
        "GET_FEEDBACKS_ICD10",
        "Get all ICD-10 feedbacks successfully!",
    )
    
    GET_FEEDBACKS_CHATBOT = (
        "GET_FEEDBACKS_CHATBOT",
        "Get all chatbot feedbacks successfully!",
    )
    
    SUBMIT_FEEDBACK_ICD10 = (
        "SUBMIT_FEEDBACK_ICD10",
        "Submit ICD-10 feedback successfully!",
    )
    
    SUBMIT_FEEDBACK_CHAPTER = (
        "SUBMIT_FEEDBACK_CHAPTER",
        "Submit chapter feedback successfully!",
    )
    
    SUBMIT_FEEDBACK_BLOCK = (
        "SUBMIT_FEEDBACK_BLOCK",
        "Submit block feedback successfully!",
    )
    
    SUBMIT_FEEDBACK_DISEASE = (
        "SUBMIT_FEEDBACK_DISEASE",
        "Submit disease feedback successfully!",
    )
    
    SUBMIT_FEEDBACK_CHATBOT = (
        "SUBMIT_FEEDBACK_CHATBOT",
        "Submit chatbot feedback successfully!",
    )
    
    ACCEPT_FEEDBACK_ICD10 = (
        "ACCEPT_FEEDBACK_ICD10",
        "Accept ICD-10 feedback successfully!",
    )
    
    ACCEPT_FEEDBACK_CHATBOT = (
        "ACCEPT_FEEDBACK_CHATBOT",
        "Accept chatbot feedback successfully!",
    )
    
    REJECT_FEEDBACK_ICD10 = (
        "REJECT_FEEDBACK_ICD10",
        "Reject ICD-10 feedback successfully!",
    )
    
    REJECT_FEEDBACK_CHATBOT = (
        "REJECT_FEEDBACK_CHATBOT",
        "Reject chatbot feedback successfully!",
    )
    
    GET_USER_FEEDBACKS_ICD10 = (
        "GET_USER_FEEDBACKS_ICD10",
        "Get user ICD-10 feedbacks successfully!",
    )
     
    GET_USER_FEEDBACKS_CHATBOT = (
        "GET_USER_FEEDBACKS_CHATBOT",
        "Get user chatbot feedbacks successfully!",
    )
    
    # NOTIFICATIONS
    GET_USER_NOTIFICATIONS = (
        "GET_USER_NOTIFICATIONS",
        "Get user notifications successfully!",
    )
    
    @classmethod
    def get_success(cls, message):
        return getattr(cls, message, cls.DEFAULT)
