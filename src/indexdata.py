import os
import google.generativeai as genai
from qdrant_client import QdrantClient
from qdrant_client.models import Distance, VectorParams, PointStruct
from langchain_text_splitters import RecursiveCharacterTextSplitter
from pypdf import PdfReader
import yaml


cfg = yaml.load(open('../config.yml', 'r'), Loader=yaml.FullLoader)

# 1. Cấu hình API
GENIMI_API_KEY = cfg['GENIMI_API_KEY']
genai.configure(api_key=GENIMI_API_KEY)
qdrant_client = QdrantClient("localhost", port=6333)

# 2. Định nghĩa Model Embedding của Gemini
EMBED_MODEL = "models/text-embedding-004"  # 768 dimensions


def create_collection(collection_name):
    """Tạo collection nếu chưa tồn tại"""
    if not qdrant_client.collection_exists(collection_name):
        qdrant_client.create_collection(
            collection_name=collection_name,
            vectors_config=VectorParams(size=768, distance=Distance.COSINE),
        )
        print(f"Đã tạo collection: {collection_name}")


def get_embedding(text):
    """Gọi Gemini API để lấy vector"""
    result = genai.embed_content(
        model=EMBED_MODEL,
        content=text,
        task_type="retrieval_document"
    )
    return result['embedding']


def process_pdf_to_qdrant(pdf_path, collection_name):
    print(f"Đang xử lý: {pdf_path} -> {collection_name}")
    create_collection(collection_name)

    # Đọc PDF
    reader = PdfReader(pdf_path)
    full_text = ""
    for page in reader.pages:
        full_text += page.extract_text()

    # Cắt nhỏ văn bản (Chunking)
    text_splitter = RecursiveCharacterTextSplitter(
        chunk_size=1000,
        chunk_overlap=100
    )
    chunks = text_splitter.split_text(full_text)

    # Chuẩn bị Points để đẩy vào Qdrant
    points = []
    for i, chunk in enumerate(chunks):
        vector = get_embedding(chunk)
        points.append(PointStruct(
            id=hash(f"{pdf_path}_{i}") & 0xFFFFFFFFFFFFFFFF,  # Tạo ID duy nhất
            vector=vector,
            payload={
                "text": chunk,
                "source": pdf_path,
                "topic": collection_name
            }
        ))

    # Upsert vào Qdrant
    qdrant_client.upsert(collection_name=collection_name, points=points)
    print(f"✨ Đã đẩy {len(points)} chunks vào {collection_name}")


# --- THỰC THI ---
if __name__ == "__main__":
    # Đẩy dữ liệu vào Topic 1: Federated Learning
    process_pdf_to_qdrant("paper_fed_learning.pdf", "topic_federated_learning")

    # Đẩy dữ liệu vào Topic 2: Reinforcement Learning
    process_pdf_to_qdrant("paper_rl.pdf", "topic_reinforcement_learning")