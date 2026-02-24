import os
import yaml
from fastmcp import FastMCP
from qdrant_client import QdrantClient
from sentence_transformers import SentenceTransformer

# =========================
# 1. Load cấu hình & Khởi tạo Model
# =========================
curr_dir = os.path.dirname(__file__)
config_path = os.path.join(curr_dir, '../..', 'config.yml')

with open(config_path, 'r', encoding='utf-8') as f:
    cfg = yaml.safe_load(f)

# SỬA ĐỔI: Sử dụng model BGE-base Local (768 dims) giống hệt lúc Index
EMBED_MODEL_NAME = "BAAI/bge-base-en-v1.5"
embed_model = SentenceTransformer(EMBED_MODEL_NAME)

# Khởi tạo MCP Server
mcp = FastMCP("Research-Gateway")
# Khởi tạo Qdrant Client
qdrant = QdrantClient(host="127.0.0.1", port=6333)


# =========================
# 2. Hàm lấy Embedding (Đồng bộ với Index)
# =========================
def get_query_embedding(text: str):
    """
    Sử dụng model local để tạo vector 768 chiều.
    Không còn phụ thuộc vào API_URL hay HF_TOKEN.
    """
    try:
        # BGE model khuyến khích thêm chỉ dẫn truy vấn để đạt độ chính xác cao nhất
        instruction_query = f"Represent this sentence for searching relevant passages: {text}"
        vector = embed_model.encode(instruction_query).tolist()
        return vector
    except Exception as e:
        print(f"❌ Lỗi tạo Embedding: {e}")
        return None


# =========================
# 3. Định nghĩa Công cụ (Tools)
# =========================
@mcp.tool()
async def search_papers(topic: str, query: str, limit: int = 5) -> str:
    """
    Tìm kiếm thông tin từ cơ sở dữ liệu paper theo topic.
    - topic: 'topic1_fl' hoặc 'topic2_sl'.
    - query: Từ khóa tìm kiếm (ví dụ: 'pfed lora').
    """
    # Xử lý trường hợp Agent gửi topic là 'both' hoặc không hợp lệ
    topics_to_search = []
    if topic == "both":
        topics_to_search = ["topic1_fl", "topic2_sl"]
    else:
        topics_to_search = [topic]

    all_results = []

    # Lấy vector cho câu truy vấn (768 dims)
    query_vector = get_query_embedding(query)
    if not query_vector:
        return "Lỗi: Không thể khởi tạo vector tìm kiếm."

    for t in topics_to_search:
        collection_name = f"collection_{t}"

        if not qdrant.collection_exists(collection_name):
            continue

        # Truy vấn Qdrant
        results = qdrant.search(
            collection_name=collection_name,
            query_vector=query_vector,
            limit=limit
        )

        for res in results:
            source = res.payload.get("source", "Unknown")
            content = res.payload.get("text", "")
            all_results.append(f"Source: {source} (Topic: {t})\nContent: {content}")

    if not all_results:
        return f"Không tìm thấy tài liệu liên quan đến '{query}'."

    return "\n\n---\n\n".join(all_results)


if __name__ == "__main__":
    mcp.run()