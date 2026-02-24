import os
import yaml
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.messages import HumanMessage, ToolMessage
from src.utils.config_loader import cfg

# Khởi tạo Gemini Flash để nhận diện ý định tìm kiếm (nhanh và rẻ)
llm = ChatGoogleGenerativeAI(
    model="gemini-2.5-flash",
    google_api_key=cfg['GOOGLE_API_KEY']
)


def citation_node(state):
    """
    Nhiệm vụ: Trích xuất keyword từ câu hỏi và chuẩn bị dữ liệu cho việc gọi MCP Tool.
    Trong LangGraph, node này sẽ chuẩn bị 'research_data' bằng cách gọi search_papers.
    """
    # 1. Lấy tin nhắn cuối cùng của người dùng từ State
    query = state["messages"][-1].content

    # 2. Yêu cầu LLM xác định nên search vào topic nào: topic1_fl hay topic2_sl
    prompt = f"""
    Dựa trên câu hỏi của người dùng: "{query}"
    Hãy xác định chủ đề nghiên cứu thuộc về:
    - 'topic1_fl' (nếu nói về Federated Learning)
    - 'topic2_sl' (nếu nói về Split Learning)
    - 'both' (nếu đề cập cả hai hoặc so sánh)

    Chỉ trả ra tên topic hoặc 'both', không giải thích thêm.
    """

    topic_decision = llm.invoke([HumanMessage(content=prompt)]).content.strip().lower()
    print(topic_decision)

    # 3. Giả lập hoặc điều hướng gọi MCP Tool (Thực tế MCP Tool được gọi thông qua mcp_server.py)
    # Trong môi trường LangGraph + MCP, kết quả từ MCP Tool search_papers
    # sẽ được đưa vào research_data.

    return {
        "next_node": topic_decision,  # Trả về topic để node sau sử dụng
        "messages": [HumanMessage(content=f"Phát hiện chủ đề: {topic_decision}")]
    }