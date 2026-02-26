import operator
from typing import Annotated, Sequence, TypedDict
from langgraph.graph import StateGraph, END

from src.agents.mcp_search_node import mcp_search_node
# Import State và các Node Agent
from src.utils.state import AgentState
from src.agents.analyst import analyst_node
from src.agents.citation import citation_node
from src.agents.gap_detector import gap_detector_node
from src.agents.idea_gen import idea_gen_node

# 1. Khởi tạo Graph với State định nghĩa trước

workflow = StateGraph(AgentState)


def route_after_analyst(state):
    intent = state.get("intent", "full_research")

    if intent == "summary_only":
        print("Router: Người dùng chỉ cần tóm tắt. Kết thúc sớm!")
        return END  # Bỏ qua Gap và Idea Gen
    else:
        print("Router: Bắt đầu phân tích sâu (Gap & Idea).")
        return "gap_detector"

# 2. Thêm các Nodes (Các bước xử lý)

workflow.add_node("citation_expert", citation_node)
workflow.add_node("mcp_search", mcp_search_node)  # Tìm dữ liệu từ Qdrant
workflow.add_node("paper_analyst", analyst_node)        # Tóm tắt nội dung
workflow.add_node("gap_detector", gap_detector_node)    # Tìm khoảng trống nghiên cứu
workflow.add_node("idea_generator", idea_gen_node)      # Đề xuất hướng mới



workflow.set_entry_point("citation_expert")
workflow.add_edge("citation_expert", "mcp_search") # Expert báo topic -> Search đi tìm
workflow.add_edge("mcp_search", "paper_analyst")   # Search có data -> Analyst làm việc
workflow.add_conditional_edges(
    "paper_analyst",       # Node xuất phát
    route_after_analyst,   # Hàm quyết định đường đi
    # Tùy chọn: Mapping kết quả hàm trả về với tên Node
    {
        "gap_detector": "gap_detector",
        END: END
    }
)
#workflow.add_edge("paper_analyst", "gap_detector")
workflow.add_edge("gap_detector", "idea_generator")
workflow.add_edge("idea_generator", END)


# Kết thúc sau khi Idea Generator hoàn thành
workflow.add_edge("idea_generator", END)

app = workflow.compile()

# Xuất sơ đồ Graph (Tùy chọn - dùng để debug)
print(app.get_graph().draw_ascii())