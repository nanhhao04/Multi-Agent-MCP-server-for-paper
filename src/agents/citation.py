import os
import yaml
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.messages import HumanMessage, ToolMessage
from src.utils.config_loader import cfg
from src.utils.config_llm import llm


def citation_node(state):
    query = state["messages"][-1].content

    # Nâng cấp Prompt: Vừa lấy topic, vừa sinh sub-queries
    prompt = f"""
    Bạn là một chuyên gia lập kế hoạch nghiên cứu AI.
    Câu hỏi của người dùng: "{query}"

    Nhiệm vụ:
    1. Xác định topic ('topic1_fl', 'topic2_sl', hoặc 'both').
    2. Đặt ra 3 câu hỏi phụ (sub-queries) bao quát các khía cạnh kỹ thuật của câu hỏi trên để tìm kiếm tài liệu.

    BẮT BUỘC TRẢ VỀ ĐÚNG FORMAT SAU (Các thành phần cách nhau bởi dấu |):
    TOPIC|Câu hỏi phụ 1|Câu hỏi phụ 2|Câu hỏi phụ 3

    Ví dụ: both|Kiến trúc cơ bản của FL|Cách SL nén dữ liệu|So sánh hiệu năng FL và SL
    """

    response = llm.invoke([HumanMessage(content=prompt)]).content.strip()

    # Xử lý chuỗi trả về để lấy dữ liệu
    parts = response.split('|')
    topic_decision = parts[0].strip().lower()

    # Nếu LLM trả về đúng định dạng, lấy các câu hỏi phụ. Nếu lỗi, lấy câu gốc.
    if len(parts) >= 2:
        sub_queries = [p.strip() for p in parts[1:] if p.strip()]
    else:
        sub_queries = [query]

    print(f"Đã xác định Topic: {topic_decision}")
    print(f"Đã sinh ra các Sub-queries: {sub_queries}")

    return {
        "topic": topic_decision,
        "sub_queries": sub_queries,
        "messages": [HumanMessage(content=f"Đang tiến hành tìm kiếm sâu đa chiều cho chủ đề: {topic_decision}")]
    }