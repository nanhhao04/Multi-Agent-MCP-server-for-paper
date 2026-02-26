import os
import yaml
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.messages import HumanMessage, ToolMessage
from src.utils.config_loader import cfg
from src.utils.config_llm import llm


def citation_node(state):
    query = state["messages"][-1].content

    prompt = f"""
    Bạn là chuyên gia điều phối nghiên cứu AI.
    Dựa vào câu hỏi: "{query}"

    1. Xác định TOPIC ('topic1_fl', 'topic2_sl', hoặc 'both').
    2. Xác định INTENT (Ý định) của người dùng:
       - 'summary_only': Nếu họ chỉ hỏi khái niệm, định nghĩa, hoặc yêu cầu tóm tắt.
       - 'full_research': Nếu họ yêu cầu so sánh sâu, tìm điểm yếu (gap), hoặc đề xuất hướng mới.
    3. Sinh ra 2-3 câu hỏi phụ (sub-queries).

    Trả về đúng định dạng: TOPIC | INTENT | Sub-query 1 | Sub-query 2
    """

    response = llm.invoke([HumanMessage(content=prompt)]).content.strip()
    parts = response.split('|')

    topic_decision = parts[0].strip().lower()
    intent_decision = parts[1].strip().lower() if len(parts) > 1 else "full_research"
    sub_queries = [p.strip() for p in parts[2:] if p.strip()] if len(parts) > 2 else [query]

    return {
        "topic": topic_decision,
        "intent": intent_decision,
        "sub_queries": sub_queries
    }