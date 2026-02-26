from typing import Annotated, Sequence, TypedDict, List, Dict, Any
import operator
from langchain_core.messages import BaseMessage


class AgentState(TypedDict):
    # messages: Lưu nhật ký hội thoại, Annotated giúp cộng dồn tin nhắn thay vì ghi đè
    messages: Annotated[Sequence[BaseMessage], operator.add]

    # research_data: Chứa nội dung thô lấy từ Qdrant
    research_data: str
    intent: str

    sub_queries : List[str]

    # summary_report: Bản tóm tắt các paper từ Analyst Agent
    summary_report: str

    # gaps: Các khoảng trống nghiên cứu từ Gap Detector
    gaps: str

    # final_proposal: Đề xuất cuối cùng từ Idea Gen Agent
    final_proposal: str

    # next_node: Điều hướng luồng chạy trong Graph
    topic: str