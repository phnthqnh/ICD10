from rest_framework.views import APIView
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated, IsAdminUser
from rest_framework.response import Response
from rest_framework import status
from ICD10.serializers.icd10_serializers import *
from ICD10.models.icd10 import *
from constants.constants import Constants
from libs.response_handle import AppResponse
from libs.Redis import RedisWrapper
from permissions.permisstions import IsAdmin, IsUser
from constants.error_codes import ErrorCodes
from constants.success_codes import SuccessCodes
from utils.utils import Utils
from ICD10.models.user import User
from django.views.decorators.cache import cache_page


@api_view(['GET'])
# @permission_classes([IsAuthenticated])
def get_icd10_chapters(request):
    try:
        # 1. Lấy dữ liệu từ cache
        cached_chapters = RedisWrapper.get(Constants.CACHE_KEY_CHAPTERS)
        if cached_chapters:
            return AppResponse.success(
                SuccessCodes.GET_CHAPTERS,
                data={
                    "chapters": cached_chapters,
                    "total": len(cached_chapters)
                }
            )
        # 2. Nếu chưa có cache -> query DB
        chapters = ICDChapter.objects.all()
        chapters_data = Utils.serialize_queryset(chapters)
        
        # 3. Lưu vào cache (ví dụ 15 phút)
        RedisWrapper.save(Constants.CACHE_KEY_CHAPTERS, chapters_data, expire_time=60*1)
        # len of data
        data_length = len(chapters_data)
        return AppResponse.success(
            SuccessCodes.GET_CHAPTERS,
            data={
                "chapters": chapters_data,
                "total": data_length
            }
        )
        
    except Exception as e:
        return AppResponse.error(ErrorCodes.UNKNOWN_ERROR, errors=str(e))
    
@api_view(['GET'])
# @permission_classes([IsAuthenticated])
def get_blocks_by_chapter(request, pk):
    try:
        # 1. Lấy dữ liệu từ cache
        cached_blocks = RedisWrapper.get(f"{Constants.CACHE_KEY_BLOCKS}_{pk}")
        if cached_blocks:
            return AppResponse.success(
                SuccessCodes.GET_BLOCKS_BY_CHAPTER,
                data={
                    "blocks": cached_blocks,
                    "total": len(cached_blocks)
                }
            )
        # 2. Nếu chưa có cache -> query DB
        chapter = ICDChapter.objects.filter(id=pk).first()
        if not chapter:
            return AppResponse.error(ErrorCodes.NOT_FOUND, errors="Chapter not found")
        
        blocks = ICDBlock.objects.filter(chapter=chapter)
        blocks_data = Utils.serialize_queryset(blocks)

        # 3. Lưu vào cache (ví dụ 15 phút)
        RedisWrapper.save(f"{Constants.CACHE_KEY_BLOCKS}_{pk}", blocks_data, expire_time=60*1)
        data_length = len(blocks_data)
        return AppResponse.success(
            SuccessCodes.GET_BLOCKS_BY_CHAPTER,
            data={
                "blocks": blocks_data,
                "total": data_length
            }
        )
        
    except Exception as e:
        return AppResponse.error(ErrorCodes.UNKNOWN_ERROR, errors=str(e))
    
@api_view(['GET'])
# @permission_classes([IsAuthenticated])
def get_diseases_by_block(request, pk):
    try:
        # 1. Lấy dữ liệu từ cache
        cached_diseases = RedisWrapper.get(f"{Constants.CACHE_KEY_DISEASES}_{pk}")
        if cached_diseases:
            return AppResponse.success(
                SuccessCodes.GET_DISEASES_BY_BLOCK,
                data={
                    "diseases": cached_diseases,
                    "total": len(cached_diseases)
                }
            )
        # 2. Nếu chưa có cache -> query DB
        block = ICDBlock.objects.filter(id=pk).first()
        if not block:
            return AppResponse.error(ErrorCodes.NOT_FOUND, errors="Block not found")
        
        diseases = ICDDisease.objects.filter(block=block, parent__isnull=True).all()
        diseases_data = Utils.serialize_queryset(diseases)
        
        # 3. Lưu vào cache (ví dụ 15 phút)
        RedisWrapper.save(f"{Constants.CACHE_KEY_DISEASES}_{pk}", diseases_data, expire_time=60*1)
        data_length = len(diseases_data)
        return AppResponse.success(
            SuccessCodes.GET_DISEASES_BY_BLOCK,
            data={
                "diseases": diseases_data,
                "total": data_length
            }
        )
        
    except Exception as e:
        return AppResponse.error(ErrorCodes.UNKNOWN_ERROR, errors=str(e))
    
@api_view(['GET'])
# @permission_classes([IsAuthenticated, IsAdmin])
def get_diseases_children(request, pk):
    try:
        # 1. Lấy dữ liệu từ cache
        cached_subdiseases = RedisWrapper.get(f"{Constants.CACHE_KEY_DISEASES_CHILDREN}_{pk}")
        if cached_subdiseases:
            return AppResponse.success(
                SuccessCodes.GET_DISEASES_CHILDREN,
                data={
                    "diseases": cached_subdiseases,
                    "total": len(cached_subdiseases)
                }
            )
        # 2. Nếu chưa có cache -> query DB
        parent_disease = ICDDisease.objects.filter(id=pk).first()
        subdisease = ICDDisease.objects.filter(parent=parent_disease).all()
        if not subdisease:
            return AppResponse.error(ErrorCodes.NOT_FOUND, errors="Subdisease not found")

        subdisease_data = Utils.serialize_queryset(subdisease)
        
        # 3. Lưu vào cache (ví dụ 15 phút)
        RedisWrapper.save(f"{Constants.CACHE_KEY_DISEASES_CHILDREN}_{pk}", subdisease_data, expire_time=60*1)
        data_length = len(subdisease_data)
        return AppResponse.success(
            SuccessCodes.GET_DISEASES_CHILDREN,
            data={
                "diseases": subdisease_data,
                "total": data_length
            }
        )
        
    except Exception as e:
        return AppResponse.error(ErrorCodes.UNKNOWN_ERROR, errors=str(e))