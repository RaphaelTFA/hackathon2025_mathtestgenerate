from openai import OpenAI
from config import LLM_API_KEY, MODEL

client = OpenAI(
    base_url="https://openrouter.ai/api/v1",
    api_key=LLM_API_KEY,
)

default_messages = [
            {"role": "developer", "content": "You are a helpful assistant."},
            {"role": "assistant", "content": "Hello! How can I assist you today?"},
            {"role": "user", "content": "Hello!"}
        ]

def call_llm(messages=default_messages, model = MODEL):
    completion = client.chat.completions.create(
        model=model,
        messages=messages,
    )
    return completion.choices[0].message.content
