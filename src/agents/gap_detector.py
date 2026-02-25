from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.messages import HumanMessage
import yaml
import os
from src.utils.config_llm import llm


def gap_detector_node(state):
    """So sánh các summary_report để tìm Gap"""
    summary = state.get("summary_report", "")

    prompt = f"""
    Dựa trên tóm tắt các nghiên cứu sau: {summary}

    Hãy phân tích và chỉ ra 3 khoảng trống nghiên cứu (Research Gaps) mà các bài báo này chưa giải quyết triệt để.
    Tập trung vào tính khả thi khi triển khai thực tế.
    """

    response = llm.invoke([HumanMessage(content=prompt)])
    return {"gaps": response.content}