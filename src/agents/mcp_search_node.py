from src.server.mcp_server import search_papers  # Import trực tiếp từ server của bạn
from src.utils.state import AgentState


async def mcp_search_node(state: AgentState):
    """Node trung gian kết nối Graph với dữ liệu Qdrant"""
    # 1. Lấy thông tin topic và query từ State
    topic = state.get("next_node", "both")

    query = state["messages"][0].content
    print(f"Query : {query} | topic : {topic}")

    # 2. Xử lý logic search cho trường hợp 'both'
    if topic == "both":
        data_fl = await search_papers(topic="topic1_fl", query=query)
        data_sl = await search_papers(topic="topic2_sl", query=query)
        final_data = f"--- FEDERATED LEARNING ---\n{data_fl}\n\n--- SPLIT LEARNING ---\n{data_sl}"
    else:
        final_data = await search_papers(topic=topic, query=query)

    # 3. Ghi dữ liệu vào research_data để Analyst có thể đọc
    return {"research_data": final_data}