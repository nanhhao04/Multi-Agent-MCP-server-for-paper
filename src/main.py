import os
import asyncio
from langchain_core.messages import HumanMessage
from src.agents.graph import app
from src.utils.config_loader import cfg





async def run_research(query: str):
    print(f"\n Khởi chạy hệ thống DRAN: {query}")
    print("-" * 50)

    initial_state = {
        "messages": [HumanMessage(content=query)],
        "research_data": "",
        "summary_report": "",
        "gaps": "",
        "final_proposal": "",
        "next_node": ""  # Thêm trường này nếu AgentState của bạn có
    }

    async for event in app.astream(initial_state):
        for node_name, output in event.items():
            print(f"\n>>> [NODE: {node_name}] COMPLETED")

            # 1. Log lỗi dữ liệu đầu vào (Cực kỳ quan trọng cho bước MCP Search)
            if "research_data" in output:
                data = output["research_data"]
                if not data or "Lỗi" in data or "Error" in data:
                    print(f"❌ LỖI DỮ LIỆU TẠI {node_name}: {data}")
                else:
                    print(f"✅ Đã lấy được dữ liệu bài báo ({len(data)} ký tự).")

            # 2. Log nội dung tóm tắt từ Analyst
            if "summary_report" in output:
                print(f"📝 Analyst Report Preview: {output['summary_report'][:150]}...")

            # 3. Log Gaps phát hiện được
            if "gaps" in output:
                print(f"🔍 Research Gaps identified: {output['gaps'][:150]}")

            # 4. Log tin nhắn điều hướng (Next Node)
            if "next_node" in output:
                print(f"📍 Điều hướng tiếp theo: {output['next_node']}")

    # Kết thúc
    print("\n" + "=" * 50)
    print("🏁 QUY TRÌNH KẾT THÚC")


if __name__ == "__main__":
    # Nhập câu hỏi nghiên cứu của bạn ở đây

    user_query = "pfed lora"

    # Chạy vòng lặp sự kiện async
    try:
        asyncio.run(run_research(user_query))
    except KeyboardInterrupt:
        print("\n Đã dừng hệ thống.")