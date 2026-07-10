import requests


# -------------------------------------------------------
# Generate Interview Questions
# -------------------------------------------------------
def generate_questions(resume_text, jd_text):

    return [
        "Tell me about your current role and responsibilities.",
        "Describe your Kubernetes experience.",
        "Explain a major production incident you handled recently.",
        "How have you implemented CI/CD pipelines?",
        "What automation projects have you worked on?"
    ]


# -------------------------------------------------------
# Generate Expected Answer
# -------------------------------------------------------
def generate_expected_answer(question):

    prompt = f"""
You are a Senior DevOps Technical Interviewer.

Question:
{question}

Provide:

1. Ideal Answer
2. Key Technical Points
3. Common Mistakes
4. Follow-up Questions

Keep the response concise and interviewer-friendly.
"""

    try:

        response = requests.post(
            "http://127.0.0.1:11434/api/generate",
            json={
                "model": "gemma:2b",
                "prompt": prompt,
                "stream": False
            },
            timeout=180
        )

        response.raise_for_status()

        return response.json().get(
            "response",
            "No response received."
        )

    except Exception as e:

        return f"Expected answer generation error: {e}"


# -------------------------------------------------------
# Generate Follow-Up Question
# -------------------------------------------------------
def generate_followup_question(question, answer):

    prompt = f"""
You are a Senior DevOps Technical Interviewer.

Original Question:
{question}

Candidate Answer:
{answer}

Generate ONE technical follow-up question that helps
the interviewer assess deeper knowledge.

Return only the follow-up question.
"""

    try:

        response = requests.post(
            "http://127.0.0.1:11434/api/generate",
            json={
                "model": "gemma:2b",
                "prompt": prompt,
                "stream": False
            },
            timeout=180
        )

        response.raise_for_status()

        return response.json().get(
            "response",
            "No response received."
        )

    except Exception as e:

        return f"Follow-up question error: {e}"


# -------------------------------------------------------
# Generate Interview Report
# -------------------------------------------------------
def generate_interview_report(responses):

    prompt = f"""
You are a senior technical interviewer.

Review the candidate responses below.

Provide:

1. Candidate Overview

2. Technical Strengths

3. Areas Requiring Validation

4. Technical Depth Observed

5. Suggested Follow-up Questions

6. Final Interview Summary

Important:
- Do not make a hiring decision
- Do not recommend hire/reject
- Focus only on technical observations
- Keep comments professional and objective

Candidate Responses:

{responses}

"""

    try:

        response = requests.post(
            "http://127.0.0.1:11434/api/generate",
            json={
                "model": "gemma:2b",
                "prompt": prompt,
                "stream": False
            },
            timeout=180
        )

        response.raise_for_status()

        return response.json().get(
            "response",
            "No response received."
        )

    except Exception as e:

        return f"Interview report error: {e}"
