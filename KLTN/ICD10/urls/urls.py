from django.urls import path
from ICD10.views import icd_views, user_views, chatbot_views, feedback_views, notification_views

urlpatterns = [
    # user endpoints
    path("register/", user_views.user_register, name="user-register"),
    path("login/", user_views.login, name="user-login"),
    path("verify-email/", user_views.verify_email, name="verify-email"),
    path("verified_doctor/<int:pk>/", user_views.verified_doctor, name="verified-doctor"),
    path("list_verification/", user_views.get_users_waiting_verification, name="list-verification"),
    path("approve_verification/<int:pk>/", user_views.approve_doctor_verification, name="approve-verification"),
    # icd10 endpoints
    path("chapters/", icd_views.get_icd10_chapters, name="chapter-list"),
    path("chapters/children/<int:pk>/", icd_views.get_blocks_by_chapter, name="blocks-by-chapter"),
    path("blocks/children/<int:pk>/", icd_views.get_diseases_by_block, name="diseases-by-block"),
    path("diseases/children/<int:pk>/", icd_views.get_diseases_children, name="diseases-children"),
    path("diseases_code/", icd_views.get_disease_code, name="disease-code"),
    path("disease/<str:code>/", icd_views.get_disease_by_code, name="disease-by-code"),
    path("search_diseases/", icd_views.search_diseases, name="search-diseases"),
    path("chat_with_ai/", chatbot_views.chat_with_ai, name="chat-with-ai"),
    # path("blocks/<str:block_code>/", icd_views.BlockDetailView.as_view(), name="block-detail"),
    # path("diseases/<str:disease_code>/", icd_views.DiseaseDetailView.as_view(), name="disease-detail"),
    # path("diseases/<str:disease_code>/subdiseases/", icd_views.SubDiseaseListView.as_view(), name="subdisease-list"),
    # path("diseases/search/", icd_views.DiseaseSearchView.as_view(), name="disease-search"),
    # feedback endpoints
    path("feedbacks/icd10/submit/", feedback_views.submit_feedback_icd, name="submit-feedback-icd10"),
    path("feedbacks/chatbot/submit/", feedback_views.submit_feedback_chatbot, name="submit-feedback-chatbot"),
    path("feedbacks/icd10/all/", feedback_views.get_all_feedbacks_icd, name="get-all-feedbacks-icd10"),
    path("feedbacks/chatbot/all/", feedback_views.get_all_feedbacks_chatbot, name="get-all-feedbacks-chatbot"),
    path("feedbacks/icd10/user/", feedback_views.get_feedbacks_icd_by_user, name="get-feedbacks-icd10-by-user"),
    path("feedbacks/chatbot/user/", feedback_views.get_feedbacks_chatbot_by_user, name="get-feedbacks-chatbot-by-user"),
    path("feedbacks/icd10/accept/<int:pk>/", feedback_views.accept_feedback_icd, name="accept-feedback-icd10"),
    path("feedbacks/chatbot/accept/<int:pk>/", feedback_views.accept_feedback_chatbot, name="accept-feedback-chatbot"),
    path("feedbacks/icd10/reject/<int:pk>/", feedback_views.reject_feedback_icd, name="reject-feedback-icd10"),
    path("feedbacks/chatbot/reject/<int:pk>/", feedback_views.reject_feedback_chatbot, name="reject-feedback-chatbot"),
    # notification endpoints
    path("notifications/unread_count/", notification_views.unread_notifications, name="unread-notifications"),
    path("notifications/user/", notification_views.user_notifications, name="user-notifications"),
]
