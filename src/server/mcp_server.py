import json
import os
import ssl

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


import urllib.request
import urllib.parse
import xml.etree.ElementTree as ET


@mcp.tool()
async def search_arxiv(query: str, max_results: int = 3) -> str:
    """
    Tìm kiếm các bài báo khoa học mới nhất từ ArXiv.
    Sử dụng khi cần cập nhật kiến thức SOTA hoặc tìm các paper chưa có trong Qdrant.
    """
    try:
        # Encode query để đưa lên URL hợp lệ
        safe_query = urllib.parse.quote(query)
        url = f'http://export.arxiv.org/api/query?search_query=all:{safe_query}&start=0&max_results={max_results}'

        ctx = ssl.create_default_context()
        ctx.check_hostname = False
        ctx.verify_mode = ssl.CERT_NONE

        # Gọi API truyền kèm ctx
        response = urllib.request.urlopen(url, context=ctx)
        data = response.read().decode('utf-8')

        # Phân tích XML trả về
        root = ET.fromstring(data)
        ns = {'atom': 'http://www.w3.org/2005/Atom'}

        results = []
        log_data = []

        for entry in root.findall('atom:entry', ns):
            title = entry.find('atom:title', ns).text.strip().replace('\n', ' ')
            summary = entry.find('atom:summary', ns).text.strip().replace('\n', ' ')
            published = entry.find('atom:published', ns).text[:10]  # Lấy YYYY-MM-DD
            author = entry.find('atom:author/atom:name', ns).text

            log_data.append({
                "query": query,
                "title": title,
                "author": author,
                "published": published,
                "summary": summary
            })

            results.append(
                f"- Tiêu đề: {title}\n- Tác giả chính: {author}\n- Xuất bản: {published}\n- Abstract: {summary}\n"
            )

        if log_data:
            curr_dir = os.path.dirname(__file__)
            log_dir = os.path.abspath(os.path.join(curr_dir, '../../log'))
            os.makedirs(log_dir, exist_ok=True)
            log_file = os.path.join(log_dir, 'arxiv.json')

            # Chỉ ghi file 1 lần duy nhất sau khi đã gom đủ data
            with open(log_file, "w", encoding="utf-8") as f:
                json.dump(log_data, f, ensure_ascii=False, indent=4)

        if not results:
            return f"Không tìm thấy bài báo nào trên ArXiv cho từ khóa '{query}'."

        return "\n".join(results)

    except Exception as e:
        return f"Lỗi khi kết nối ArXiv API: {str(e)}"


@mcp.tool()
async def search_papers(topic: str, query: str, limit: int = 5) -> str:
    topics_to_search = []
    if topic == "both":
        topics_to_search = ["topic1_fl", "topic2_sl"]
    else:
        topics_to_search = [topic]

    all_results = []


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