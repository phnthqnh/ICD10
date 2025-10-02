from rest_framework import serializers
from ICD10.models.icd10 import *

class ChapterSerializer(serializers.ModelSerializer):
    class Meta:
        model = ICDChapter
        fields = '__all__'

class BlockSerializer(serializers.ModelSerializer):
    chapter = ChapterSerializer(read_only=True)

    class Meta:
        model = ICDBlock
        fields = '__all__'

class DiseaseSerializer(serializers.ModelSerializer):
    # block = BlockSerializer(read_only=True)
    parent = serializers.SerializerMethodField()

    class Meta:
        model = ICDDisease
        fields = '__all__'

    def get_parent(self, obj):
        if obj.parent:
            return {
                "code": obj.parent.code,
                "title": obj.parent.title
            }
        return None
    

class DiseaseExtraInfoSerializer(serializers.ModelSerializer):
    disease = DiseaseSerializer(read_only=True)

    class Meta:
        model = DiseaseExtraInfo
        fields = '__all__'
        

