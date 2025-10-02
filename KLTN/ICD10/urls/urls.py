from django.urls import path
from ICD10.views import icd_views, user_views

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
    # path("blocks/<str:block_code>/", icd_views.BlockDetailView.as_view(), name="block-detail"),
    # path("diseases/<str:disease_code>/", icd_views.DiseaseDetailView.as_view(), name="disease-detail"),
    # path("diseases/<str:disease_code>/subdiseases/", icd_views.SubDiseaseListView.as_view(), name="subdisease-list"),
    # path("diseases/search/", icd_views.DiseaseSearchView.as_view(), name="disease-search"),
]
