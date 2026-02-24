from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.messages import HumanMessage
import yaml
import os

# Load config
curr_dir = os.path.dirname(__file__)
with open(os.path.join(curr_dir, '../../config.yml'), 'r', encoding='utf-8') as f:
    cfg = yaml.safe_load(f)

llm = ChatGoogleGenerativeAI(model="gemini-2.5-flash", google_api_key=cfg['GOOGLE_API_KEY'])


def analyst_node(state):
    """
    Expert-level analysis of research papers focusing on FL, SL, and Distributed AI.
    """
    # Lấy dữ liệu từ state (đã được MCP Search đổ vào)
    context = state.get("research_data", "")

    # Prompt chuyên gia tiếng Anh
    prompt = f"""
    You are a Senior Research Scientist specializing in Distributed Artificial Intelligence, 
    specifically Federated Learning (FL) and Split Learning (SL). 

    Your task is to conduct a deep technical analysis of the following research context:
    ---
    {context}
    ---

    Please extract and synthesize the information into a professional report with the following structure:

    1. **Research Problem**: Identify the core challenge being addressed (e.g., privacy concerns, communication bottlenecks, or non-IID data issues).
    2. **Proposed Methodology**: Detail the technical approach. Specify if it involves architectural changes (SL), novel aggregation strategies (FL), or hybrid mechanisms.
    3. **Key Contributions**: Highlight the primary breakthroughs (e.g., improved convergence rate, reduced energy consumption, or enhanced privacy guarantees).
    4. **Critical Limitations**: Identify technical gaps or constraints (e.g., scalability limits, vulnerability to model poisoning, or computational overhead).

    Requirement: Provide a concise, highly technical summary using professional academic terminology.
    """

    # Gọi LLM xử lý
    response = llm.invoke([HumanMessage(content=prompt)])

    # Ghi kết quả vào summary_report để Gap Detector tiếp tục xử lý
    return {"summary_report": response.content}