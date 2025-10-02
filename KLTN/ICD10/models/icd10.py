from django.db import models


class ICDChapter(models.Model):
    """
    Chương lớn trong ICD-10 (ví dụ: I: Certain infectious and parasitic diseases)
    """
    code = models.CharField(max_length=10, unique=True)  # VD: "I"
    title = models.CharField(max_length=255)             # VD: "Certain infectious and parasitic diseases"
    description = models.TextField(blank=True, null=True)

    def __str__(self):
        return f"{self.code} - {self.title}"
    
    class Meta:
        app_label = "ICD10"
        db_table = "icd_chapter"


class ICDBlock(models.Model):
    """
    Nhóm bệnh trong 1 chương (block)
    """
    code = models.CharField(max_length=20)         # VD: "A00-A09"
    title = models.CharField(max_length=255)             # VD: "Intestinal infectious diseases"
    description = models.TextField(blank=True, null=True)
    chapter = models.ForeignKey(ICDChapter, on_delete=models.CASCADE, related_name="blocks")

    def __str__(self):
        return f"{self.code} - {self.title}"

    class Meta:
        app_label = "ICD10"
        db_table = "icd_block"

class ICDDisease(models.Model):
    """
    Mã bệnh cụ thể trong ICD-10
    """
    code = models.CharField(max_length=10, unique=True)  # VD: "A01.0"
    code_no_sign = models.CharField(max_length=10)    # VD: "A010" (không dấu chấm)
    title = models.CharField(max_length=255)             # VD: "Typhoid fever"
    description = models.TextField(blank=True, null=True)
    block = models.ForeignKey(ICDBlock, on_delete=models.CASCADE, related_name="diseases")
    updated_at = models.DateTimeField(null=True, blank=True)
    
    # Quan hệ cha-con (disease grouping trong ICD)
    parent = models.ForeignKey("self", on_delete=models.SET_NULL, null=True, blank=True, related_name="sub_diseases")

    def __str__(self):
        return f"{self.code} - {self.title}"
    
    class Meta:
        app_label = "ICD10"
        db_table = "icd_disease"


class DiseaseExtraInfo(models.Model):
    """
    Bảng mở rộng để enrich dữ liệu từ Wikipedia, v.v.
    """
    disease = models.OneToOneField(ICDDisease, on_delete=models.CASCADE, related_name="extra_info")
    wikipedia_url = models.URLField(blank=True, null=True)
    image_url = models.URLField(blank=True, null=True)
    symptoms = models.TextField(blank=True, null=True)
    treatment = models.TextField(blank=True, null=True)
    causes = models.TextField(blank=True, null=True)

    def __str__(self):
        return f"Extra info for {self.disease.code}"

    class Meta:
        app_label = "ICD10"
        db_table = "disease_extra_info"