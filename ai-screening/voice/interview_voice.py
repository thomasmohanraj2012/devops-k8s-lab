import requests

OLLAMA_URL = "http://127.0.0.1:11434/api/generate"

def evaluate_answer(question, answer):

    prompt = f"""
You are a DevOps interviewer.

Question:
{question}

Candidate Answer:
{answer}

Provide:

1. Score out of 10
2. Strengths
3. Gaps
4. Follow-up Question
"""

    response = requests.post(
        OLLAMA_URL,
        json={
            "model": "gemma:2b",
            "prompt": prompt,
            "stream": False
        },
        timeout=180
    )

    return response.json()["response"]
