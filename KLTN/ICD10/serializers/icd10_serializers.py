from rest_framework import serializers
from ICD10.models.icd10 import *

class ChapterSerializer(serializers.ModelSerializer):
    class Meta:
        model = ICDChapter
        fields = ['id', 'chapter', 'code', 'title_vi']

class BlockSerializer(serializers.ModelSerializer):
    chapter = ChapterSerializer(read_only=True)

    class Meta:
        model = ICDBlock
        fields =['id', 'code', 'title_vi', 'chapter']

class DiseaseSerializer(serializers.ModelSerializer):
    block = BlockSerializer(read_only=True)
    # parent = serializers.SerializerMethodField()
    is_leaf = serializers.SerializerMethodField()

    class Meta:
        model = ICDDisease
        fields = ['id', 'code', 'title_vi', 'is_leaf', 'block']

    # def get_parent(self, obj):
    #     if obj.parent:
    #         return {
    #             "code": obj.parent.code,
    #             "title": obj.parent.title
    #         }
    #     return None
    
    def get_is_leaf(self, obj):
        return not ICDDisease.objects.filter(parent=obj).exists()
    

class DiseaseExtraInfoSerializer(serializers.ModelSerializer):
    disease = DiseaseSerializer(read_only=True)

    class Meta:
        model = DiseaseExtraInfo
        fields = ['id', 'wikipedia_url', 'description', 'symptoms', 'image_url', 'disease']
        

