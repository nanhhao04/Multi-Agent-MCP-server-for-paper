from fastmcp import FastMCP
from qdrant_client import QdrantClient
# Import helper lấy embedding của bạn ở đây

mcp = FastMCP("Research-Vault")
qdrant = QdrantClient("localhost", port=6333)

@mcp.tool()
async def search_papers(topic_name: str, query: str):
    """Tìm kiếm tài liệu theo topic (ví dụ: 'wireless' hoặc 'ai')"""
    # Logic: query qdrant và trả về text
    return f"Kết quả tìm kiếm cho {query} trong {topic_name}..."

if __name__ == "__main__":
    mcp.run()