import os
import yaml
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.messages import HumanMessage
from src.utils.config_llm import llm



def analyst_node(state):

    context = state.get("research_data", "").strip()

    if not context or "Lỗi:" in context or "Không tìm thấy" in context:
        error_msg = "Không có đủ dữ liệu hợp lệ từ bài báo để phân tích. Vui lòng kiểm tra lại từ khóa tìm kiếm hoặc kết nối Qdrant."
        print(f"Analyst Node cảnh báo: Hệ thống không nhận được dữ liệu thô hợp lệ.")
        return {"summary_report": error_msg}

    print(f"\nAnalyst Agent đang tổng hợp khối ngữ cảnh đa chiều ({len(context)} ký tự)...")

    prompt = f"""
    You are a Senior Research Scientist specializing in Distributed Artificial Intelligence, 
    specifically Federated Learning (FL) and Split Learning (SL). 

    You are provided with an aggregated knowledge base compiled from multiple vector searches (Deep Research) 
    targeting different sub-aspects of a user's query. 

    Your task is to cross-reference, synthesize, and conduct a deep technical analysis of the following context:
    ---
    {context}
    ---

    Please extract and synthesize the scattered information into a unified, highly professional academic report 
    using the following strict structure:

    1. **Research Problem**: Identify the core challenges being addressed across the provided excerpts (e.g., privacy leaks, communication bottlenecks, non-IID data issues).
    2. **Proposed Methodology**: Detail the technical approaches mentioned. Explain how they work (e.g., specific architectural changes, novel aggregation strategies like pFedLoRA, gradient compression).
    3. **Key Contributions**: Highlight the primary breakthroughs and performance improvements supported by the text (e.g., reduced communication overhead by X%, improved convergence rate).
    4. **Critical Limitations**: Identify technical gaps, constraints, or trade-offs explicitly stated or strongly implied in the text.

    Requirement: 
    - Base your analysis STRICTLY on the provided context. Do not hallucinate external knowledge.
    - Provide a concise, highly technical summary using professional academic terminology.
    - If certain information (like Limitations) is completely missing from the context, explicitly state "Not mentioned in the provided excerpts."
    """

    response = llm.invoke([HumanMessage(content=prompt)])

    print("Analyst Agent đã hoàn thành bản tóm tắt chuyên sâu.")
    return {"summary_report": response.content}