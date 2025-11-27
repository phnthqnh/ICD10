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
from ICD10.serializers.icd10_serializers import *
from ICD10.models.user import User
from django.views.decorators.cache import cache_page
from django.db.models import Q
import re
import logging
# Khởi tạo logger
logger = logging.getLogger(__name__)

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
        # chapters_data = Utils.serialize_queryset(chapters, fields=["id", "chapter", "code", "title_en", "title_vi"])
        chapters_data = ChapterSerializer(chapters, many=True).data
        
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
        # blocks_data = Utils.serialize_queryset(blocks)
        blocks_data = BlockDataSerializer(blocks, many=True).data

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
        # diseases_data = Utils.serialize_queryset(diseases)
        diseases_data = DiseaseDataSerializer(diseases, many=True).data
        # thêm trường is_leaf vào data
        
        
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

        # subdisease_data = Utils.serialize_queryset(subdisease)
        subdisease_data = DiseaseDataSerializer(subdisease, many=True).data
        
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
    
@api_view(['GET'])
def get_disease_code(request):
    try:
        # 1. Lấy dữ liệu từ cache
        cached_disease = RedisWrapper.get(Constants.CACHE_KEY_DISEASES_CODE)
        if cached_disease:
            return AppResponse.success(
                SuccessCodes.GET_DISEASE_CODE,
                data={
                    "diseases": cached_disease,
                    "total": len(cached_disease)
                }
            )
        # 2. Nếu chưa có cache -> query DB
        diseases = ICDDisease.objects.all()
        diseases_data = Utils.serialize_queryset(diseases, fields=["code"])
        
        # 3. Lưu vào cache (ví dụ 15 phút)
        RedisWrapper.save(Constants.CACHE_KEY_DISEASES_CODE, diseases_data, expire_time=60*1)
        # len of data
        data_length = len(diseases_data)
        return AppResponse.success(
            SuccessCodes.GET_DISEASE_CODE,
            data={
                "diseases": diseases_data,
                "total": data_length
            }
        )
        
    except Exception as e:
        return AppResponse.error(ErrorCodes.UNKNOWN_ERROR, errors=str(e))


@api_view(['GET'])
def get_disease_by_code(request, code):
    try:
        # 1. Lấy dữ liệu từ cache
        cached_disease = RedisWrapper.get(f"{Constants.CACHE_KEY_DISEASES_BY_CODE}_{code}")
        if cached_disease:
            return AppResponse.success(
                SuccessCodes.GET_DISEASE_BY_CODE,
                data=cached_disease
            )
        # 2. Nếu chưa có cache -> query DB
        disease = ICDDisease.objects.filter(code=code).first()
        disease_extra = DiseaseExtraInfo.objects.filter(disease=disease).first()
        if not disease:
            return AppResponse.error(ErrorCodes.NOT_FOUND, errors="Disease not found")
        
        disease_data = Utils.serialize_extrainfo_queryset([disease], fields=["code", "title_en", "title_vi"])
        disease_data[0]["description"] = disease_extra.description
        disease_data[0]["symptoms"] = disease_extra.symptoms
        disease_data[0]["image_url"] = disease_extra.image_url
        disease_data[0]["wikipedia_url"] = disease_extra.wikipedia_url
        if disease.parent:
            parent_data = Utils.serialize_queryset([disease.parent], fields=["code", "title_en", "title_vi"])
            disease_data[0]["parent"] = parent_data[0]
        else:
            disease_data[0]["parent"] = None
        
        # 3. Lưu vào cache (ví dụ 15 phút)
        RedisWrapper.save(f"{Constants.CACHE_KEY_DISEASES_BY_CODE}_{code}", disease_data[0], expire_time=60*1)
        return AppResponse.success(
            SuccessCodes.GET_DISEASE_BY_CODE,
            data=disease_data[0]
        )
        
    except Exception as e:
        return AppResponse.error(ErrorCodes.UNKNOWN_ERROR, errors=str(e))
    
    


# api search diseases by query string
@api_view(["GET"])
def search_diseases(request):
    query = request.GET.get("q", "").strip()
    if not query:
        return AppResponse.error(ErrorCodes.INVALID_REQUEST, errors="Query parameter 'q' is required.")
    try:
        # Search in ICDDisease and related DiseaseExtraInfo
        diseases = ICDDisease.objects.filter(
            Q(title_en__icontains=query) |
            Q(title_vi__icontains=query) |
            Q(code__icontains=query) |
            Q(extra_info__description__icontains=query) |
            Q(extra_info__symptoms__icontains=query)
        ).distinct()

        if not diseases:
            return AppResponse.error(ErrorCodes.NOT_FOUND, errors="No diseases found matching the query.")

        diseases_data = []
        for disease in diseases:
            disease_data = Utils.serialize_queryset([disease])[0]
            # Add extra info if available
            extra_info = DiseaseExtraInfo.objects.filter(disease=disease).first()
            if extra_info:
                disease_data['description'] = extra_info.description
                disease_data['symptoms'] = extra_info.symptoms
                disease_data['image_url'] = extra_info.image_url
                disease_data['wikipedia_url'] = extra_info.wikipedia_url
            diseases_data.append(disease_data)

        return AppResponse.success(
            SuccessCodes.SEARCH_DISEASES,
            data={
                "diseases": diseases_data,
                "total": len(diseases_data)
            }
        )
    except Exception as e:
        return AppResponse.error(ErrorCodes.UNKNOWN_ERROR, errors=str(e))
    
@api_view(["GET"])
def autocomplete_diseases(request):
    query = request.GET.get("q", "").strip()
    if not query:
        return Response({"suggestions": []})
    # Escape regex để không bị lỗi ký tự đặc biệt
    escaped_query = re.escape(query)
    
    # Tìm chính xác từ/cụm trong câu
    # \b không hoạt động tốt với tiếng Việt → dùng lookaround
    pattern = rf"(?<!\w){escaped_query}(?!\w)"
    diseases = (
        ICDDisease.objects.filter(
            Q(code__icontains=query) |
            Q(title_vi__iregex=pattern)
        )
        .order_by("code")
    )
    

    data = []
    
    for d in diseases:
        level = 3 if d.parent else 2
        data.append({
            "id": d.id,
            "code": d.code,
            "title_vi": d.title_vi,
            "level": level
        })

    return Response({"suggestions": data})

    
@api_view(['GET'])
# @permission_classes([IsAuthenticated])
def get_data_chapter(request, pk):
    try:
        # 1. Lấy dữ liệu từ cache
        cache_chapter = RedisWrapper.get(f"{Constants.CACHE_DATA_CHAPTER}_CHAPTER_{pk}")
        cached_blocks = RedisWrapper.get(f"{Constants.CACHE_DATA_CHAPTER}_BLOCK_{pk}")
        if cached_blocks:
            return AppResponse.success(
                SuccessCodes.GET_DATA_CHAPTER,
                data={
                    "chapter": cache_chapter,
                    "children": cached_blocks
                }
            )
        # 2. Nếu chưa có cache -> query DB
        chapter = ICDChapter.objects.filter(id=pk).first()
        if not chapter:
            return AppResponse.error(ErrorCodes.NOT_FOUND, errors="Chapter not found")
        
        chapter_data = ChapterSerializer(chapter).data
        blocks = ICDBlock.objects.filter(chapter=chapter)
        blocks_data = Utils.serialize_queryset(blocks)

        # 3. Lưu vào cache (ví dụ 15 phút)
        RedisWrapper.save(f"{Constants.CACHE_DATA_CHAPTER}_BLOCK_{pk}", blocks_data, expire_time=60*1)
        RedisWrapper.save(f"{Constants.CACHE_DATA_CHAPTER}_CHAPTER_{pk}", chapter_data, expire_time=60*1)
        return AppResponse.success(
            SuccessCodes.GET_DATA_CHAPTER,
            data={
                "chapter": chapter_data,
                "children": blocks_data
            }
        )
        
    except Exception as e:
        return AppResponse.error(ErrorCodes.UNKNOWN_ERROR, errors=str(e))
    
@api_view(['GET'])
# @permission_classes([IsAuthenticated])
def get_data_block(request, pk):
    try:
        # 1. Lý dữ liệu từ cache
        cached_diseases = RedisWrapper.get(f"{Constants.CACHE_DATA_BLOCK}_DISEASES_{pk}")
        cached_block = RedisWrapper.get(f"{Constants.CACHE_DATA_BLOCK}_BLOCK_{pk}")
        if cached_diseases:
            return AppResponse.success(
                SuccessCodes.GET_DATA_BLOCK,
                data={
                    "block": cached_block,
                    "children": cached_diseases
                }
            )
        # 2. Nếu chưa có cache -> query DB
        block = ICDBlock.objects.filter(id=pk).first()
        if not block:
            return AppResponse.error(ErrorCodes.NOT_FOUND, errors="Block not found")
        
        block_data = BlockSerializer(block).data
        diseases = ICDDisease.objects.filter(block=block, parent__isnull=True).all()
        diseases_data = Utils.serialize_queryset(diseases)

        # 3. Lưu vào cache (ví dụ 15 phút)
        RedisWrapper.save(f"{Constants.CACHE_DATA_BLOCK}_DISEASES_{pk}", diseases_data, expire_time=60*1)
        RedisWrapper.save(f"{Constants.CACHE_DATA_BLOCK}_BLOCK_{pk}", block_data, expire_time=60*1)
        
        return AppResponse.success(
            SuccessCodes.GET_DATA_BLOCK,
            data={
                "block": block_data,
                "children": diseases_data
            }
        )
        
    except Exception as e:
        return AppResponse.error(ErrorCodes.UNKNOWN_ERROR, errors=str(e))
    
@api_view(['GET'])
# @permission_classes([IsAuthenticated])
def get_data_disease(request, pk):
    try:
        # 1. Lý dữ liệu từ cache
        cached_disease = RedisWrapper.get(f"{Constants.CACHE_DATA_DISEASE}_DISEASE_{pk}")
        cached_children = RedisWrapper.get(f"{Constants.CACHE_DATA_DISEASE}_CHILDREN_{pk}")
        if cached_children:
            return AppResponse.success(
                SuccessCodes.GET_DATA_DISEASE,
                data={
                    "disease": cached_disease,
                    "children": cached_children,
                }
            )
        # 2. Nếu chưa có cache -> query DB
        disease = ICDDisease.objects.filter(id=pk).first()
        if not disease:
            return AppResponse.error(ErrorCodes.NOT_FOUND, errors="Disease not found")
        
        disease_data = DiseaseSerializer(disease).data
        children = ICDDisease.objects.filter(parent=disease).all()
        children_data = Utils.serialize_queryset(children)

        # 3. Lưu vào cache (ví dụ 15 phút)
        RedisWrapper.save(f"{Constants.CACHE_DATA_DISEASE}_CHILDREN_{pk}", children_data, expire_time=60*1)
        RedisWrapper.save(f"{Constants.CACHE_DATA_DISEASE}_DISEASE_{pk}", disease_data, expire_time=60*1)
        
        return AppResponse.success(
            SuccessCodes.GET_DATA_DISEASE,
            data={
                "disease": disease_data,
                "children": children_data,
            }
        )
        
    except Exception as e:
        return AppResponse.error(ErrorCodes.UNKNOWN_ERROR, errors=str(e))
    
    
@api_view(['GET'])
# @permission_classes([IsAuthenticated])
def get_data_disease_child(request, pk):
    try:
        # 1. Lý dữ liệu từ cache
        cached_disease_parent = RedisWrapper.get(f"{Constants.CACHE_DATA_DISEASE}_DISEASE_PARENT_{pk}")
        cached_diseases = RedisWrapper.get(f"{Constants.CACHE_DATA_DISEASE}_DISEASES_SAME_PARENT_{pk}")
        cached_disease = RedisWrapper.get(f"{Constants.CACHE_DATA_DISEASE}_DISEASE_{pk}")
        if cached_disease:
            return AppResponse.success(
                SuccessCodes.GET_DATA_DISEASE,
                data={
                    "disease_parent": cached_disease_parent,
                    "disease": cached_disease,
                    "children": cached_diseases
                }
            )
        # 2. Nếu chưa có cache -> query DB
        disease = ICDDisease.objects.filter(id=pk).first()
        if not disease:
            return AppResponse.error(ErrorCodes.NOT_FOUND, errors="Disease not found")
        
        disease_data = DiseaseSerializer(disease).data
        # Get parent
        disease_parent = ICDDisease.objects.filter(id=disease.parent_id).first()
        disease_parent_data = DiseaseSerializer(disease_parent).data
        
        # get same parent except current
        diseases = ICDDisease.objects.filter(parent=disease_parent).exclude(id=disease.id).all()
        diseases_data = Utils.serialize_queryset(diseases)

        # 3. Lưu vào cache (ví dụ 15 phút)
        RedisWrapper.save(f"{Constants.CACHE_DATA_DISEASE}_DISEASE_{pk}", disease_data, expire_time=60*1)
        RedisWrapper.save(f"{Constants.CACHE_DATA_DISEASE}_DISEASE_PARENT_{pk}", disease_parent_data, expire_time=60*1)
        RedisWrapper.save(f"{Constants.CACHE_DATA_DISEASE}_DISEASES_SAME_PARENT_{pk}", diseases_data, expire_time=60*1)
        
        return AppResponse.success(
            SuccessCodes.GET_DATA_DISEASE,
            data={
                "disease_parent": disease_parent_data,
                "disease": disease_data,
                "children": diseases_data
            }
        )
        
    except Exception as e:
        return AppResponse.error(ErrorCodes.UNKNOWN_ERROR, errors=str(e))


@api_view(["GET"])
def get_chapter(request):
    """
    Lấy tất cả chapter ICD-10
    """
    cached_chapter = RedisWrapper.get(f"{Constants.CACHE_DATA_CHAPTER}_ALL")
    if cached_chapter:
        return AppResponse.success(
            SuccessCodes.GET_CHAPTERS,
            data={
                "chapters": cached_chapter
            },
        )
    chapters = ICDChapter.objects.all().order_by("code")
    chapters_data = Utils.serialize_queryset_chapter(chapters)
    RedisWrapper.save(f"{Constants.CACHE_DATA_CHAPTER}_ALL", chapters_data, expire_time=60*1)
    return AppResponse.success(
        SuccessCodes.GET_CHAPTERS,
        data={
            "chapters": chapters_data
        }
    )
    
@api_view(["GET"])
def get_block(request):
    """
    Lấy tất cả block ICD-10
    """
    cached_block = RedisWrapper.get(f"{Constants.CACHE_DATA_BLOCK}_ALL")
    if cached_block:
        return AppResponse.success(
            SuccessCodes.GET_BLOCKS_BY_CHAPTER,
            data={
                "blocks": cached_block
            },
        )
    blocks = ICDBlock.objects.all().order_by("code")
    blocks_data = Utils.serialize_queryset(blocks)
    RedisWrapper.save(f"{Constants.CACHE_DATA_BLOCK}_ALL", blocks_data, expire_time=60*1)
    return AppResponse.success(
        SuccessCodes.GET_BLOCKS_BY_CHAPTER,
        data={
            "blocks": blocks_data
        }
    )
    
@api_view(["GET"])
def get_disease(request):
    """
    Lấy tất cả disease ICD-10
    """
    cached_disease = RedisWrapper.get(f"{Constants.CACHE_DATA_DISEASE}_ALL")
    if cached_disease:
        return AppResponse.success(
            SuccessCodes.GET_DISEASE_BY_CODE,
            data={
                "diseases": cached_disease
            },
        )
    # lấy diseases parent is null
    diseases = ICDDisease.objects.filter(parent__isnull=True).order_by("code")
    diseases_data = Utils.serialize_queryset(diseases)
    RedisWrapper.save(f"{Constants.CACHE_DATA_DISEASE}_ALL", diseases_data, expire_time=60*1)
    return AppResponse.success(
        SuccessCodes.GET_DISEASE_BY_CODE,
        data={
            "diseases": diseases_data
        }
    )