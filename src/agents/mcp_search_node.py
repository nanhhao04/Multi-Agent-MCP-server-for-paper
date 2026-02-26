from src.server.mcp_server import search_papers, search_arxiv  # Import trực tiếp từ server của bạn
from src.utils.state import AgentState


async def mcp_search_node(state):
    # 1. Lấy danh sách sub-queries từ State (do Citation Agent sinh ra)
    original_query = state["messages"][0].content
    print(f"Original query: {original_query}")

    sub_queries = state.get("sub_queries", [])
    if not sub_queries:
        original_query = state["messages"][0].content
        print(f"Original query: {original_query}")
        sub_queries = [original_query]

    topic = state.get("topic", "both")
    print(f"\nBẮT ĐẦU TRUY XUẤT SÂU (DEEP SEARCH) | Topic: {topic}")
    print(f"Tổng số Sub-queries cần tìm: {len(sub_queries)}")

    accumulated_data = ""

    # 2. Vòng lặp: Quét Qdrant cho TỪNG sub-query để không bỏ sót khía cạnh nào
    for i, sq in enumerate(sub_queries):
        print(f"Đang quét Qdrant cho sub-query {i + 1}: '{sq}'...")

        if topic == "both":
            data_fl = await search_papers(topic="topic1_fl", query=sq)
            data_sl = await search_papers(topic="topic2_sl", query=sq)

            sq_result = (
                f"--- FEDERATED LEARNING ---\n{data_fl}\n\n"
                f"--- SPLIT LEARNING ---\n{data_sl}"
            )
        else:
            sq_result = await search_papers(topic=topic, query=sq)

        # 3. Gom (Aggregate) dữ liệu lại, đánh dấu rõ ràng từng phần cho Analyst dễ đọc
        accumulated_data += f"\n\n{'=' * 20}\n"
        accumulated_data += f"NGỮ CẢNH TRÍCH XUẤT TỪ QDRANT CHO: '{sq}'\n"
        accumulated_data += f"{'=' * 20}\n"
        accumulated_data += f"{sq_result}\n"

    data_arxiv = await search_arxiv(query=original_query)
    accumulated_data += f"\n\n{'=' * 20}\n"
    accumulated_data += f"Các bài paper liên quan: '{data_arxiv}'\n"


    # 4. Ghi toàn bộ khối lượng tri thức khổng lồ này vào research_data
    print(f"Hoàn thành Deep Search. Tổng dung lượng ngữ cảnh: {len(accumulated_data)} ký tự.")
    return {"research_data": accumulated_data.strip()}