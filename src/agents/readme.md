##  Kiến trúc Luồng Multi-Agent 

Hệ thống DRAN sử dụng LangGraph để điều phối một luồng làm việc tự động (Autonomous Workflow) giữa các Agent đóng vai trò là các chuyên gia nghiên cứu. Luồng dữ liệu chạy tuần tự và bồi đắp tri thức thông qua `AgentState`.

**Sơ đồ luồng thực thi (Execution Flow):**
`User Query` ➔ **Citation Agent** ➔ **MCP Search** ➔ **Analyst Agent** ➔ **Gap Detector** ➔ **Idea Generator** ➔ `Final Proposal`

### Chi tiết Nhiệm vụ từng Node:
1. **Citation Node (Chuyên gia Lập kế hoạch):** - Phân tích câu hỏi gốc của người dùng.
   - Phân loại chủ đề nghiên cứu (`topic1_fl`, `topic2_sl` hoặc `both`).
   - Sinh ra các câu hỏi phụ (sub-queries) để phục vụ cho tìm kiếm sâu.
2. **MCP Search Node (Cổng Truy xuất Dữ liệu):** - Đóng vai trò là cầu nối (Tool Node) gọi tới MCP Server.
   - Quét cơ sở dữ liệu vector Qdrant dựa trên topic và sub-queries.
   - Gom cụm (Aggregate) các đoạn văn bản kỹ thuật thành một khối ngữ cảnh lớn (`research_data`).
3. **Analyst Node (Chuyên gia Phân tích):** - Đọc khối dữ liệu `research_data`.
   - Trích xuất 4 thành phần cốt lõi: Vấn đề (Problem), Phương pháp (Method), Đóng góp (Contributions), và Hạn chế (Limitations).
   - Xuất ra một báo cáo tóm tắt chuyên sâu (`summary_report`).
4. **Gap Detector Node (Chuyên gia Phản biện):** - Phân tích `summary_report` để tìm ra những điểm mâu thuẫn hoặc chưa hoàn thiện của các bài báo trước đó.
   - Trích xuất 3 khoảng trống nghiên cứu (Research Gaps) mang tính khả thi thực tế.
5. **Idea Gen Node (Chuyên gia Sáng tạo):** - Nhận "đầu vào" là các Gaps.
   - Đề xuất kiến trúc hoặc hướng nghiên cứu đột phá nhằm giải quyết các hạn chế đã nêu.