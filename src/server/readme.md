# MCP Research Tools Specification

### 1. Tool: `search_papers`
- **Mục tiêu**: Tìm kiếm các đoạn văn bản (chunks) có độ tương đồng cao nhất từ Qdrant.
- **Tham số**: 
    - `topic` (string): 'topic1_fl' hoặc 'topic2_sl'.
    - `query` (string): Nội dung cần tìm.
- **Output**: Danh sách các đoạn văn bản kèm nguồn (source file).

### 2. Tool: `get_paper_metadata`
- **Mục tiêu**: Trích xuất thông tin tổng quan về các file đã có trong database để Agent biết mình đang có gì.
- **Tham số**: `topic` (string).
- **Output**: Danh sách tên các file PDF đã index trong collection đó.

### 3. Tool: `read_full_context`
- **Mục tiêu**: Lấy toàn bộ các chunks của một file PDF cụ thể để phân tích sâu (thay vì chỉ lấy vài đoạn similarity).
- **Tham số**: `source_name` (string), `topic` (string).
- **Output**: Toàn bộ nội dung văn bản của file đó.