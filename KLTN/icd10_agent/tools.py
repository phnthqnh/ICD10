import json
import numpy as np
from sklearn.metrics.pairwise import cosine_similarity
from typing import Any
from google import genai
from google.genai import types
import base64
import os
from constants.constants import Constants
from dotenv import load_dotenv
load_dotenv()
from ICD10.models.icd10 import ICDDisease, ICDBlock


# ------------------------------------------------------
# LOAD DỮ LIỆU ICD10 + EMBEDDING
# ------------------------------------------------------

with open("icd_core_embedding.json", "r", encoding="utf-8") as f:
    ICD_RECORDS: list[dict[str, Any]] = json.load(f)

ICD_EMBEDS = np.array([rec["embedding"] for rec in ICD_RECORDS], dtype=np.float32)

ICD_RECORDS_CLEAN = [
    {
        "stt_chuong": rec["stt_chuong"],
        "ma_chuong": rec["ma_chuong"],
        "chapter_name": rec["chapter_name"],
        "ten_chuong": rec["ten_chuong"],
        "ma_nhom_chinh": rec["ma_nhom_chinh"],
        "main_group_name_i": rec["main_group_name_i"],
        "ten_nhom_chinh": rec["ten_nhom_chinh"],
        "ma_nhom_phu_1": rec["ma_nhom_phu_1"],
        "sub_group_name_i": rec["sub_group_name_i"],
        "ten_nhom_phu_1": rec["ten_nhom_phu_1"],
        "ma_nhom_phu_2": rec["ma_nhom_phu_2"],
        "sub_group_name_ii": rec["sub_group_name_ii"],
        "ten_nhom_phu_2": rec["ten_nhom_phu_2"],
        "ma_loai": rec["ma_loai"],
        "type_name": rec["type_name"],
        "ten_loai": rec["ten_loai"],
        "ma_benh": rec["ma_benh"],
        "disease_name": rec["disease_name"],
        "ten_benh": rec["ten_benh"],
    }
    for rec in ICD_RECORDS
]

# tool 1: predict_icd10
# def predict_keyword(text_query: str) -> str:
#     """
#     Predict disease (keywords)
    
#     Phân tích triệu chứng từ text query → sinh keyword.
    
#     Lưu ý: Nếu user gửi kèm ảnh, agent sẽ tự phân tích ảnh 
#     và tổng hợp thông tin trước khi gọi tool này.
    
#     :param query_emb: Chuỗi truy vấn để tìm kiếm các mã ICD khớp.

#     :type query_emb: str

#     :return: Danh sách các keyword tương ứng với mô tả hoặc hình ảnh.
#     :rtype: str
#     """

        
#     parts = []
#     prompt_text = Constants.PROMPT_AI_IMAGE.replace("{text_query}", text_query)
#     parts.append({"text": prompt_text})
#     client = genai.Client(api_key=os.getenv("GOOGLE_API_KEY"))

#     res = client.models.generate_content(
#         model="gemini-2.5-flash",
#         contents=[{"parts": parts}]
#     )
    
#     print('res', res)
#     keywords_raw = res.text  # hoặc res.candidates[0].content.parts[0].text
#     print('keywords_raw:', keywords_raw)

#     keywords_list = json.loads(keywords_raw)
#     print('keywords_list:', keywords_list)

#     keywords = ", ".join(keywords_list)
#     print('keywords:', keywords)
#     return keywords
    


def search_icd10(query: str, top_k=20) -> list[dict[str, Any]]:
    """
    Tìm kiếm mã ICD dựa trên chuỗi truy vấn.

    Chức năng này truy xuất các bản ghi mã ICD phù hợp nhất với chuỗi truy vấn đã cho,
    dựa trên độ tương đồng của embedding. Nó sử dụng một tập hợp các embedding mã ICD được định nghĩa trước (được nhúng với loại tác vụ RETRIEVAL_DOCUMENT) và so sánh chúng với embedding truy vấn (được nhúng với loại tác vụ RETRIEVAL_QUERY),
    được tạo bằng API Embedding của Gemini. Nó trả về top_k mã ICD hàng đầu được xếp hạng theo độ tương đồng.

    Bạn nên sử dụng từ khóa làm truy vấn để tối ưu hóa kết quả.

    Ghi chú:
    RETRIEVAL_DOCUMENT: Embedding được tối ưu hóa cho tìm kiếm tài liệu.
    RETRIEVAL_QUERY: Embedding được tối ưu hóa cho các truy vấn tìm kiếm chung. Sử dụng RETRIEVAL_QUERY cho các truy vấn; RETRIEVAL_DOCUMENT cho các tài liệu cần truy xuất.

    :param query: Chuỗi truy vấn để tìm kiếm các mã ICD phù hợp.
    :type query: str
    :param top_k: Số lượng kết quả phù hợp hàng đầu cần truy xuất. Mặc định là 5.
    :type top_k: int, tùy chọn
    :return: Một danh sách các từ điển chứa top_k bản ghi mã ICD phù hợp hàng đầu.
    :rtype: list[dict[str, Any]]
    """
    client = genai.Client(api_key=os.getenv("EMBEDDING_API_KEY"))
    query_emb = client.models.embed_content(
        model="gemini-embedding-001",
        contents=query,
        config=types.EmbedContentConfig(task_type="RETRIEVAL_QUERY"),
    ).embeddings[0].values
    assert query_emb and len(query_emb) > 0
    vector = np.array(query_emb)
    similarities = cosine_similarity([vector], ICD_EMBEDS)[0]
    indices = np.argsort(similarities)[::-1]

    return [ICD_RECORDS_CLEAN[i] for i in indices[:top_k]]


def predict_icd10(query: str, top_k=5) -> list[dict[str, Any]]:
    """
    Tìm kiếm mã ICD dựa trên hình ảnh.
    Lưu ý: Nếu user gửi kèm ảnh, agent sẽ tự phân tích ảnh 
    và tổng hợp thông tin trước khi gọi tool này.
    
    Chức năng này truy xuất các bản ghi mã ICD phù hợp nhất với hình ảnh và chuỗi truy vấn đã cho,
    dựa trên độ tương đồng của embedding. Nó sử dụng một tập hợp các embedding mã ICD được định nghĩa trước (được nhúng với loại tác vụ RETRIEVAL_DOCUMENT) và so sánh chúng với embedding truy vấn (được nhúng với loại tác vụ RETRIEVAL_QUERY),
    được tạo bằng API Embedding của Gemini. Nó trả về top_k mã ICD hàng đầu được xếp hạng theo độ tương đồng.

    Bạn nên sử dụng từ khóa làm truy vấn để tối ưu hóa kết quả.
    
    Ghi chú:
    RETRIEVAL_DOCUMENT: Embedding được tối ưu hóa cho tìm kiếm tài liệu.
    RETRIEVAL_QUERY: Embedding được tối ưu hóa cho các truy vấn tìm kiếm chung. Sử dụng RETRIEVAL_QUERY cho các truy vấn; RETRIEVAL_DOCUMENT cho các tài liệu cần truy xuất.

    :param query: Chuỗi truy vấn để tìm kiếm các mã ICD phù hợp.
    :type query: str
    :param top_k: Số lượng kết quả phù hợp hàng đầu cần truy xuất. Mặc định là 5.
    :type top_k: int, tùy chọn
    :return: Một danh sách các từ điển chứa top_k bản ghi mã ICD phù hợp hàng đầu.
    :rtype: list[dict[str, Any]]
    
    """
    client = genai.Client(api_key=os.getenv("EMBEDDING_API_KEY"))
    query_emb = client.models.embed_content(
        model="gemini-embedding-001",
        contents=[query],
        config=types.EmbedContentConfig(task_type="RETRIEVAL_QUERY"),
    ).embeddings[0].values
    assert query_emb and len(query_emb) > 0
    vector = np.array(query_emb)
    similarities = cosine_similarity([vector], ICD_EMBEDS)[0]
    indices = np.argsort(similarities)[::-1]

    return [ICD_RECORDS_CLEAN[i] for i in indices[:top_k]]

def get_info_icd10(code: str) -> dict[str, Any] | None:
    """
    Truy xuất hồ sơ bệnh án dựa trên mã ICD được cung cấp. Phương thức này truy vấn một tập hợp
    hồ sơ bệnh án được xác định trước được tải từ tệp JSON. Nếu tìm thấy kết quả khớp với
    mã ICD được chỉ định, bản ghi tương ứng sẽ được trả về. Nếu không tìm thấy kết quả khớp, phương thức
    trả về None.

    :param code: Mã ICD cần tìm kiếm trong hồ sơ bệnh án.

    :type code: str

    :return: Hồ sơ bệnh án được liên kết với mã ICD được cung cấp, hoặc None nếu không có
    bản ghi nào tồn tại cho mã được cung cấp.

    :rtype: dict[str, Any] | None
    """
    for rec in ICD_RECORDS:
        if rec["ma_benh"] == code:
            return {
                k: v for k, v in rec.items() if k != "embedding"
            }
    return None
