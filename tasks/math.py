from handler.llm import call_llm
from config import MODEL

content = {
    'DS' : "Dayso",
    'HKG' : "HinhKhongGian",
    'LG' : "Luonggiac",
    'ML' : "MuLoga",
    'HS' : "HamSo",
    'NHTP' : "NguyenHamTichPhan",
    'Vec' : "Vector",
    'Oxyz' : 'Oxyz',
    'XS' : "XacSuat",
    'TK' : "ThongKe",
    'DT' : "DoThi"
}

def generate_math(type = 'DS'):
    with open(f"tasks/math_content/{content[type]}.txt", "r", encoding="utf-8") as f:
        text_content = f.read()
    sample_prompt = [
            {"role": "developer", "content": "You are a helpful assistant."},
            {"role": "assistant", "content": "Hello! How can I assist you today?"},
            {"role": "user", "content": text_content},
        ]

    response = call_llm(messages=sample_prompt, model = MODEL)
    return response 
