from django.apps import AppConfig


class Icd10Config(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'ICD10'
    verbose_name = "Quản lý mã bệnh ICD-10"
    
    def ready(self):
        import ICD10.signals  # Đảm bảo các tín hiệu được đăng ký khi ứng dụng sẵn sàng
