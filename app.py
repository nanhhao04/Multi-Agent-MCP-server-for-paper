import json
import asyncio
from flask import Flask, render_template, request, Response
from langchain_core.messages import HumanMessage
from src.agents.graph import app as research_graph

app = Flask(__name__)


@app.route('/')
def index():
    return render_template('index.html')


@app.route('/ask_stream', methods=['POST'])
def ask_stream():  # Bỏ chữ 'async' ở đây đi
    data = request.json
    user_query = data.get('query', '')

    # Hàm generator ĐỒNG BỘ để Flask có thể đọc được
    def generate():
        initial_state = {
            "messages": [HumanMessage(content=user_query)],
            "research_data": "",
            "summary_report": "",
            "gaps": "",
            "final_proposal": "",
            "sub_queries": [],
            "topic": ""
        }

        # 1. Tạo một event loop mới cho thread hiện tại của Flask
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)

        # 2. Lấy bộ lặp bất đồng bộ từ LangGraph
        agen = research_graph.astream(initial_state)

        # 3. Kéo dữ liệu từng bước bằng vòng lặp while thay vì async for
        while True:
            try:
                # Ép tiến trình chạy và đợi kết quả của 1 Node
                event = loop.run_until_complete(agen.__anext__())

                for node_name, output in event.items():
                    if node_name == "citation_expert":
                        yield json.dumps({
                            "node": "citation",
                            "data": output.get("sub_queries", [])
                        }) + "\n"

                    elif node_name == "paper_analyst":
                        yield json.dumps({
                            "node": "analyst",
                            "data": output.get("summary_report", "")
                        }) + "\n"

                    elif node_name == "gap_detector":
                        yield json.dumps({
                            "node": "gap",
                            "data": output.get("gaps", "")
                        }) + "\n"

                    elif node_name == "idea_generator":
                        msg = output["messages"][-1].content if "messages" in output else ""
                        yield json.dumps({
                            "node": "idea",
                            "data": msg
                        }) + "\n"

            except StopAsyncIteration:
                # Khi Graph chạy xong toàn bộ các Agent
                break
            except Exception as e:
                print(f"Lỗi khi Stream: {e}")
                break

        loop.close()

    # Flask bây giờ sẽ nhận một generator đồng bộ tiêu chuẩn và không báo lỗi nữa
    return Response(generate(), mimetype='application/x-ndjson')


if __name__ == '__main__':
    app.run(debug=True, port=5000)