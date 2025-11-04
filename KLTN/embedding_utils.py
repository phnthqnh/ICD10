# search_disease.py
import os
import django

# --- Khởi tạo Django ---
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'KLTN.settings')  # đổi 'KLTN' thành tên project của bạn
django.setup()

# --- Import model sau khi setup ---
from sentence_transformers import SentenceTransformer
import faiss
import numpy as np
from ICD10.models.icd10 import ICDDisease, DiseaseExtraInfo

# --- Load model ngôn ngữ ---
# model = SentenceTransformer('sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2')
model = SentenceTransformer("intfloat/multilingual-e5-base")

# --- Dữ liệu ---
texts = []
codes = []
diseases = ICDDisease.objects.all()
for d in diseases:
    extra_info = DiseaseExtraInfo.objects.filter(disease=d).first()
    if extra_info:
        texts.append(f"{d.code} - {d.title_vi} - {extra_info.description or ''} - {extra_info.symptoms or ''}")
    else:
        texts.append(f"{d.code} - {d.title_vi}")
    codes.append(d.code)
    

print(f"✅ Đã tải {len(texts)} bệnh ICD10.")

batch_size = 64
embeddings = []

for i in range(0, len(texts), batch_size):
    batch_texts = texts[i:i + batch_size]
    batch_embeddings = model.encode(
        [f"query: {t}" for t in batch_texts],
        convert_to_numpy=True,
        normalize_embeddings=True
    )
    embeddings.append(batch_embeddings)

    # Log tiến trình mỗi 500 bản ghi
    if i % 500 == 0:
        print(f"✅ Đã encode {i}/{len(texts)} bệnh...")

# Gộp lại
embeddings = np.vstack(embeddings)
print(f"✅ Hoàn tất encode {len(embeddings)} embeddings, kích thước {embeddings.shape[1]}.")

# ============================================================
# 💾 3. Tạo FAISS Index (cosine similarity)
# ============================================================

dimension = embeddings.shape[1]

# 🧠 Option A: Dạng full precision (chính xác nhất, tốn RAM hơn)
index = faiss.IndexFlatIP(dimension)

# 🧠 Option B: Dạng nén IVF (giảm RAM, tốc độ nhanh hơn khi dữ liệu lớn)
# quantizer = faiss.IndexFlatIP(dimension)
# index = faiss.IndexIVFFlat(quantizer, dimension, 100)
# index.train(embeddings)

index.add(embeddings)

# ============================================================
# 📦 4. Lưu index và dữ liệu hỗ trợ
# ============================================================
faiss.write_index(index, "icd10_index_vi.faiss")
np.save("icd10_texts_vi.npy", np.array(texts, dtype=object))
np.save("icd10_codes.npy", np.array(codes, dtype=object))

print("🎉 Đã lưu xong:")
print("   ├── icd10_index_vi.faiss")
print("   ├── icd10_texts_vi.npy")
print("   └── icd10_codes.npy")

# ============================================================
# 🧪 5. Kiểm tra thử
# ============================================================
index = faiss.read_index("icd10_index_vi.faiss")
texts = np.load("icd10_texts_vi.npy", allow_pickle=True)
codes = np.load("icd10_codes.npy", allow_pickle=True)

print(f"🧪 Kiểm tra lại: có {len(codes)} bệnh, index chứa {index.ntotal} vectors.")

# Ví dụ truy vấn thử
query = "ho, sốt, đau đầu"
query_emb = model.encode([f"query: {query}"], convert_to_numpy=True, normalize_embeddings=True)
scores, idxs = index.search(query_emb, 5)

print("\n🔍 Kết quả tìm kiếm gần nhất:")
for rank, i in enumerate(idxs[0]):
    print(f"#{rank+1}: {codes[i]} | {texts[i][:120]}...")

