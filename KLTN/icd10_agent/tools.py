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

# Tạo map mã bệnh → mô tả để get info
ICD_MAP = {rec["ma_benh"]: rec for rec in ICD_RECORDS}


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
    được tạo bằng API Embedding của Gemini. Nó trả về k mã ICD hàng đầu được xếp hạng theo độ tương đồng.

    Bạn nên sử dụng từ khóa làm truy vấn để tối ưu hóa kết quả.

    Ghi chú:
    RETRIEVAL_DOCUMENT: Embedding được tối ưu hóa cho tìm kiếm tài liệu.
    RETRIEVAL_QUERY: Embedding được tối ưu hóa cho các truy vấn tìm kiếm chung. Sử dụng RETRIEVAL_QUERY cho các truy vấn; RETRIEVAL_DOCUMENT cho các tài liệu cần truy xuất.

    :param query: Chuỗi truy vấn để tìm kiếm các mã ICD phù hợp.
    :type query: str
    :param k: Số lượng kết quả phù hợp hàng đầu cần truy xuất. Mặc định là 20.
    :type k: int, tùy chọn
    :return: Một danh sách các từ điển chứa k bản ghi mã ICD phù hợp hàng đầu.
    :rtype: list[dict[str, Any]]
    """
    client = genai.Client(api_key=os.getenv("GOOGLE_API_KEY"))
    query_emb = client.models.embed_content(
        model="gemini-embedding-001",
        contents=query,
        config=types.EmbedContentConfig(task_type="RETRIEVAL_QUERY"),
    ).embeddings[0].values
    assert query_emb and len(query_emb) > 0
    vector = np.array(query_emb)
    similarities = cosine_similarity([vector], ICD_EMBEDS)[0]
    indices = np.argsort(similarities)[::-1]

    return [ICD_RECORDS[i] for i in indices[:top_k]]


def predict_icd10(query: str, top_k=20) -> list[dict[str, Any]]:
    """
    Phân tích triệu chứng từ query -> trả về top_k ICD-10 liên quan.
    Lưu ý: Nếu user gửi kèm ảnh, agent sẽ tự phân tích ảnh 
    và tổng hợp thông tin trước khi gọi tool này.
    
    :param query_emb: Chuỗi truy vấn để tìm kiếm các mã ICD khớp.

    :type query_emb: str

    :param top_k: Số lượng kết quả khớp hàng đầu cần truy xuất. Mặc định là 20.
    :type top_k: int, tùy chọn
    :return: Danh sách các từ điển chứa top_k bản ghi mã ICD khớp hàng đầu.
    :rtype: list[dict[str, Any]]
    
    """
    client = genai.Client(api_key=os.getenv("GOOGLE_API_KEY"))
    query_emb = client.models.embed_content(
        model="gemini-embedding-001",
        contents=[query],
        config=types.EmbedContentConfig(task_type="RETRIEVAL_QUERY"),
    ).embeddings[0].values
    query_emb = np.array(query_emb)
    similarities = cosine_similarity([query_emb], ICD_EMBEDS)[0]
    top_idx = np.argsort(similarities)[::-1][:top_k]

    results = []
    for idx in top_idx:
        r = ICD_RECORDS[idx]
        results.append({
            "code": r["ma_benh"],
            "name": r["ten_benh"],
            "score": round(float(similarities[idx] * 100), 2)
        })

    return results

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
            rec.pop("embedding", None)
            return rec
    return None
