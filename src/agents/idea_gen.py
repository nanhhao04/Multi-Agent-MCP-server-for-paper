from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.messages import HumanMessage
import yaml
import os

with open(os.path.join(os.path.dirname(__file__), '../../config.yml'), 'r', encoding='utf-8') as f:
    cfg = yaml.safe_load(f)

llm = ChatGoogleGenerativeAI(model="gemini-2.5-flash", google_api_key=cfg['GOOGLE_API_KEY'])


def idea_gen_node(state):
    """Đề xuất hướng nghiên cứu mới từ Gaps"""
    gaps = state.get("gaps", "")

    prompt = f"""
    Với các khoảng trống nghiên cứu sau: {gaps}

    Hãy đề xuất 1 hướng nghiên cứu mới đột phá. 
    Mô tả chi tiết kiến trúc sơ bộ và lý do tại sao hướng đi này giải quyết được các Gap trên.
    """

    response = llm.invoke([HumanMessage(content=prompt)])
    return {"messages": [response]}