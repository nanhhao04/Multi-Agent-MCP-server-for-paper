import os
import asyncio
import yaml
from flask import Flask, render_template, request, jsonify
from langchain_core.messages import HumanMessage

# Import Graph và cấu hình từ Project của bạn
from src.agents.graph import app as research_graph
from src.utils.config_loader import cfg

app = Flask(__name__)


# Hàm xử lý logic chạy Multi-Agent
async def run_research_flow(query: str):
    """
    Kích hoạt LangGraph với trạng thái ban đầu.
    """
    initial_state = {
        "messages": [HumanMessage(content=query)],
        "research_data": "",
        "summary_report": "",
        "gaps": "",
        "final_proposal": "",
        "next_node": ""
    }

    # Thực thi toàn bộ quy trình A2A (Agent-to-Agent)
    final_state = await research_graph.ainvoke(initial_state)
    return final_state


@app.route('/')
def index():
    """Trả về giao diện HTML thuần"""
    return render_template('index.html')


@app.route('/ask', methods=['POST'])
def ask():
    """API nhận câu hỏi từ giao diện và trả về JSON"""
    data = request.json
    user_query = data.get('query', '')

    if not user_query:
        return jsonify({"error": "Query is empty"}), 400

    # Chạy quy trình bất đồng bộ (Async) trong môi trường Flask
    try:
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        final_state = loop.run_until_complete(run_research_flow(user_query))
        loop.close()

        # Trả về các trường dữ liệu để hiển thị lên các Card tương ứng trên UI
        return jsonify({
            "summary": final_state.get("summary_report", "Không có dữ liệu tóm tắt."),
            "gaps": final_state.get("gaps", "Không tìm thấy khoảng trống nghiên cứu."),
            "proposal": final_state["messages"][-1].content if final_state["messages"] else "Không có đề xuất."
        })
    except Exception as e:
        return jsonify({"error": str(e)}), 500


if __name__ == '__main__':
    # Chạy server tại localhost:5000
    app.run(debug=True, port=5000)