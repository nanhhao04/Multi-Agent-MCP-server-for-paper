import yaml
from langchain_google_genai import ChatGoogleGenerativeAI
import os

# 1. Load cấu hình từ file config.yml
curr_dir = os.path.dirname(__file__)
config_path = os.path.abspath(os.path.join(curr_dir, '../../config.yml'))


def connect_llm():
    with open(config_path, 'r', encoding='utf-8') as f:
        cfg = yaml.safe_load(f)

    # 2. Khởi tạo LLM duy nhất cho toàn bộ project
    llm = ChatGoogleGenerativeAI(
        model="gemini-2.5-flash",
        google_api_key=cfg['GOOGLE_API_KEY'],
        temperature=0.2
    )
    print(" Đã khởi tạo LLM (gemini-2.5-flash) thành công.")
    return llm

llm = connect_llm()