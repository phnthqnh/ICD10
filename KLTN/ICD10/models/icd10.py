from django.db import models


class ICDChapter(models.Model):
    """
    Chương lớn trong ICD-10 (ví dụ: I: Certain infectious and parasitic diseases)
    """
    chapter = models.CharField(max_length=10, unique=True)
    code = models.CharField(max_length=10, unique=True)  # VD: "I"
    title_en = models.CharField(max_length=255)             # VD: "Certain infectious and parasitic diseases"
    title_vi = models.CharField(max_length=255)
    description = models.TextField(blank=True, null=True)

    def __str__(self):
        return f"{self.chapter} - {self.code} - {self.title_vi}"

    class Meta:
        verbose_name = 'Chương'
        verbose_name_plural = 'Chương'
        app_label = "ICD10"
        db_table = "icd_chapter"
        ordering = ["chapter"]
        indexes = [
            models.Index(fields=["chapter"], name="icd_chapter_codeS_idx"),
        ]


class ICDBlock(models.Model):
    """
    Nhóm bệnh trong 1 chương (block)
    """
    code = models.CharField(max_length=20)         # VD: "A00-A09"
    title_en = models.CharField(max_length=255)             # VD: "Intestinal infectious diseases"
    title_vi = models.CharField(max_length=255)
    description = models.TextField(blank=True, null=True)
    chapter = models.ForeignKey(ICDChapter, on_delete=models.CASCADE, related_name="blocks")

    def __str__(self):
        return f"{self.code} - {self.title_vi}"

    class Meta:
        verbose_name = 'Nhóm bệnh'
        verbose_name_plural = 'Nhóm bệnh'
        app_label = "ICD10"
        db_table = "icd_block"
        ordering = ["code"]
        indexes = [
            models.Index(fields=["code"], name="icd_block_codeS_idx"),
        ]

class ICDDisease(models.Model):
    """
    Mã bệnh cụ thể trong ICD-10
    """
    code = models.CharField(max_length=10, unique=True)  # VD: "A01.0"
    code_no_sign = models.CharField(max_length=10)    # VD: "A010" (không dấu chấm)
    title_en = models.CharField(max_length=255)             # VD: "Typhoid fever"
    title_vi = models.CharField(max_length=255)
    block = models.ForeignKey(ICDBlock, on_delete=models.CASCADE, related_name="diseases")
    updated_at = models.DateTimeField(null=True, blank=True)
    
    # Quan hệ cha-con (disease grouping trong ICD)
    parent = models.ForeignKey("self", on_delete=models.SET_NULL, null=True, blank=True, related_name="sub_diseases")

    def __str__(self):
        return f"{self.code} - {self.title_vi}"
    
    class Meta:
        verbose_name = 'Bệnh'
        verbose_name_plural = 'Các bệnh'
        app_label = "ICD10"
        db_table = "icd_disease"
        ordering = ["code"]
        indexes = [
            models.Index(fields=["code"], name="icd_disease_codeS_idx"),
        ]


class DiseaseExtraInfo(models.Model):
    """
    Bảng mở rộng để enrich dữ liệu từ Wikipedia, v.v.
    """
    disease = models.OneToOneField(ICDDisease, on_delete=models.CASCADE, related_name="extra_info")
    wikipedia_url = models.URLField(blank=True, null=True)
    description = models.TextField(blank=True, null=True)
    symptoms = models.TextField(blank=True, null=True)
    image_url = models.TextField(blank=True, null=True)

    def __str__(self):
        return f"{self.disease.code} - {self.disease.title_vi}"

    class Meta:
        verbose_name = 'Thông tin mở rộng về bệnh'
        verbose_name_plural = 'Thông tin mở rộng về bệnh'
        app_label = "ICD10"
        db_table = "disease_extra_info"