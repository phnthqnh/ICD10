from rest_framework import serializers
from ICD10.models.icd10 import *

class ChapterSerializer(serializers.ModelSerializer):
    is_leaf = serializers.SerializerMethodField()
    level = serializers.SerializerMethodField()

    def get_is_leaf(self, obj):
        return not ICDBlock.objects.filter(chapter=obj).exists()
    
    def get_level(self, obj):
        return 0
    
    class Meta:
        model = ICDChapter
        fields = ['id', 'chapter', 'code', 'title_vi', 'is_leaf', 'level']

class BlockSerializer(serializers.ModelSerializer):
    chapter = ChapterSerializer(read_only=True)
    is_leaf = serializers.SerializerMethodField()

    def get_is_leaf(self, obj):
        return not ICDDisease.objects.filter(block=obj).exists()

    class Meta:
        model = ICDBlock
        fields =['id', 'code', 'title_vi', 'chapter', 'is_leaf']

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
        
        
class BlockDataSerializer(serializers.ModelSerializer):
    is_leaf = serializers.SerializerMethodField()
    level = serializers.SerializerMethodField()

    def get_is_leaf(self, obj):
        return not ICDDisease.objects.filter(block=obj).exists()
    
    def get_level(self, obj):
        return 1

    class Meta:
        model = ICDBlock
        fields =['id', 'code', 'title_vi', 'is_leaf', 'level']
class DiseaseDataSerializer(serializers.ModelSerializer):
    is_leaf = serializers.SerializerMethodField()
    level = serializers.SerializerMethodField()

    class Meta:
        model = ICDDisease
        fields = ['id', 'code', 'title_vi', 'is_leaf', 'level']
    def get_is_leaf(self, obj):
        return not ICDDisease.objects.filter(parent=obj).exists()
    
    def get_level(self, obj):
        if obj.parent:
            return 3
        return 2