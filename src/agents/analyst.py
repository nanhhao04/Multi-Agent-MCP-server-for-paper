import os
import yaml
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.messages import HumanMessage
from src.utils.config_llm import llm


def analyst_node(state):
    # Lấy dữ liệu từ State
    context = state.get("research_data", "").strip()
    intent = state.get("intent", "full_research")  # Mặc định là nghiên cứu sâu nếu không rõ
    original_query = state["messages"][0].content  # Lấy lại câu hỏi gốc của user

    # Xử lý lỗi nếu không có context
    if not context or "Lỗi:" in context or "Không tìm thấy" in context:
        error_msg = "Không có đủ dữ liệu hợp lệ từ bài báo để phân tích. Vui lòng kiểm tra lại từ khóa tìm kiếm."
        print(f"Analyst Node cảnh báo: Hệ thống không nhận được dữ liệu thô hợp lệ.")
        return {"summary_report": error_msg}

    print(f"\nAnalyst Agent (Mode: {intent}) đang tổng hợp ({len(context)} ký tự)...")

    if intent == "summary_only":
        prompt = f"""
                Bạn là một Trợ lý Nghiên cứu AI xuất sắc, am hiểu sâu về Hệ thống phân tán (Federated Learning / Split Learning).
                Người dùng đang yêu cầu tra cứu/tóm tắt về: "{original_query}"

                Dưới đây là các tài liệu kỹ thuật được trích xuất từ cơ sở dữ liệu nội bộ và các bài báo SOTA trên ArXiv:
                ---
                {context}
                ---

                Nhiệm vụ:
                Hãy cung cấp một câu trả lời TỔNG QUAN, ĐẦY ĐỦ Ý VÀ CHUYÊN SÂU để giải đáp trọn vẹn câu hỏi của người dùng. 
                Mặc dù không cần viết thành báo cáo hàn lâm 4 phần cứng nhắc, nhưng TUYỆT ĐỐI KHÔNG trả lời quá sơ sài 1-2 câu. Hãy tận dụng tối đa các thông số và chi tiết kỹ thuật có trong ngữ cảnh.

                Hãy cấu trúc câu trả lời bằng Markdown một cách mạch lạc. Gợi ý cấu trúc (hãy linh hoạt điều chỉnh dựa trên dữ liệu thực tế):

                ###  Giải đáp trực diện
                [Trả lời thẳng vào câu hỏi gốc của người dùng: Khái niệm này là gì, hoặc nó có gì đặc biệt?]

                ###  Cơ chế hoạt động / Đặc điểm kỹ thuật
                [Trích xuất các chi tiết kỹ thuật, thuật toán, hoặc kiến trúc được nhắc đến trong ngữ cảnh. Ví dụ: Nó nén gradient ra sao? Xử lý Non-IID như thế nào?]

                ###  Lợi ích & Hiệu năng
                [Liệt kê các ưu điểm, số liệu cải thiện (nếu có) mà các bài báo đã chứng minh.]

                Yêu cầu bắt buộc:
                - Bám sát 100% vào ngữ cảnh được cung cấp. Không tự sinh hoang tưởng (hallucination).
                - Sử dụng bullet points (gạch đầu dòng) và in đậm (bold) các keyword kỹ thuật để dễ đọc.
                - Nếu ngữ cảnh hoàn toàn không có thông tin cho một phần nào đó, hãy bỏ qua phần đó thay vì tự bịa ra.
                """
    else:
        prompt = f"""
        You are a Senior Research Scientist specializing in Distributed Artificial Intelligence (FL/SL). 
        The user is researching the following topic: "{original_query}"

        You are provided with an aggregated knowledge base from Qdrant and ArXiv:
        ---
        {context}
        ---

        Your task is to conduct a deep technical analysis focused on the user's research topic. 
        Extract and synthesize the information into a professional report with this STRICT structure:

        1. **Research Problem**: Identify the core challenges addressed across the provided excerpts.
        2. **Proposed Methodology**: Detail the technical approaches and architectures mentioned.
        3. **Key Contributions**: Highlight breakthroughs and performance improvements (cite metrics if available).
        4. **Critical Limitations**: Identify technical gaps, constraints, or trade-offs explicitly stated or implied.

        Requirement: 
        - Base your analysis STRICTLY on the provided context. Do not hallucinate.
        - Provide a highly technical summary using academic terminology.
        - Trả lời bằng tiếng việt
        """

    # Gọi LLM xử lý
    response = llm.invoke([HumanMessage(content=prompt)])

    print("Analyst Agent đã hoàn thành nhiệm vụ.")
    return {"summary_report": response.content}