
from speech.transcriber import transcribe_audio
from audio_recorder_streamlit import audio_recorder
import streamlit as st
from pypdf import PdfReader
import re
import plotly.express as px
import requests
from gtts import gTTS
import tempfile
import os

st.set_page_config(
    page_title="TalentCopilot AI",
    page_icon="🚀",
    layout="wide"
)

st.markdown("""
<style>

/* Main Background */
.stApp {
    background-color: #F5F7FA;
}

/* KPI Cards */
[data-testid="stMetric"] {
    background: white;
    padding: 15px;
    border-radius: 12px;
    box-shadow: 0px 2px 10px rgba(0,0,0,0.1);
}

/* Buttons */
.stButton > button {
    width: 100%;
    border-radius: 10px;
    background-color: #1976D2;
    color: white;
    font-weight: bold;
}

/* Sidebar */
section[data-testid="stSidebar"] {
    background-color: #0F172A;
}

section[data-testid="stSidebar"] * {
    color: white;
}

/* Upload Area */
[data-testid="stFileUploader"] {
    background-color: white;
    padding: 15px;
    border-radius: 10px;
}

</style>
""", unsafe_allow_html=True)



from interview.interview_engine import (
    generate_questions,
    generate_expected_answer,
    generate_followup_question,
    generate_interview_report
)

from interview.answer_evaluator import evaluate_candidate_answer



# -------------------------------------------------------
# Application UI
# -------------------------------------------------------

if st.button("Test Audio"):

    st.audio("test.mp3")

menu = st.sidebar.radio(
    "Navigation",
    [
        "🏠 Dashboard",
        "📄 Resume Screening",
        "🎤 Interview Copilot",
        "📊 Analytics"
    ]
)

if menu == "🏠 Dashboard":

    # st.markdown("""
    # <div style="
    #     background: linear-gradient(90deg,#1976D2,#42A5F5);
    #     padding:25px;
    #     border-radius:15px;
    #     text-align:center;
    #     margin-bottom:20px;
    # ">
    #     <h1 style="color:white;">
    #         🚀 TalentCopilot AI
    #     </h1>

    #     <h4 style="color:white;">
    #         AI Powered Talent Intelligence Platform
    #     </h4>
    # </div>
    # """, unsafe_allow_html=True)

    st.header("📊 Executive Dashboard")

    col1,col2,col3,col4 = st.columns(4)

    col1.metric("👤 Candidates","12")
    col2.metric("🎯 Avg Score","84%")
    col3.metric("🤖 Questions Generated","48")
    col4.metric("✅ Hiring Readiness","High")

    st.markdown("### Hiring Pipeline")

    col1,col2,col3 = st.columns(3)

    with col1:
        st.success("""
        ✅ Shortlisted

        7 Candidates
        """)

    with col2:
        st.warning("""
        ⏳ Under Review

        3 Candidates
        """)

    with col3:
        st.error("""
        ❌ Rejected

        2 Candidates
        """)

    # ADD THIS SECTION NEXT
    st.info("""
    👋 Welcome to TalentCopilot AI

    This platform helps recruiters:

    ✅ Screen resumes

    ✅ Generate AI interviews

    ✅ Conduct voice assessments

    ✅ Evaluate candidate responses

    ✅ Generate hiring recommendations
    """)

# -------------------------------------------------------
# Skill Dictionary
# -------------------------------------------------------
SKILLS = [
    "aws", "gcp", "azure", "terraform", "kubernetes", "docker", "helm",
    "jenkins", "gitlab", "github", "argocd", "ansible", "splunk",
    "prometheus", "grafana", "python", "bash", "linux", "nginx",
    "mongodb", "mysql", "dynamodb", "rds", "sonarqube", "nexus",
    "trivy", "veracode", "eks", "iam", "sre", "devsecops",
    "vault", "openshift", "gitops", "cloud build", "artifact registry",
    "harbor", "jfrog", "s3", "route 53", "vpc", "waf", "kms",
    "secrets manager", "cloud monitoring", "shell scripting", "yaml"
]

# -------------------------------------------------------
# Ollama AI Assessment Function
# -------------------------------------------------------
def generate_ai_assessment(resume_text, job_description, match_score, matched, missing):
    prompt = f"""
You are an AI technical recruiter assistant.

Important instructions:
- This is only a screening support summary.
- Do not make a final hiring decision.
- Provide fair, job-related assessment only.
- Focus only on skills, experience, projects, tools, and job requirements.
- Avoid personal, demographic, or non-job-related comments.

Resume Text:
{resume_text[:5000]}

Job Description:
{job_description}

Match Score:
{match_score}%

Matched Skills:
{", ".join(sorted(matched)) if matched else "None"}

Missing Skills:
{", ".join(sorted(missing)) if missing else "None"}

Generate a structured recruiter assessment with the following sections:

1. Candidate Summary
2. Key Strengths
3. Skills Matched Against Job Description
4. Skills / Areas to Validate
5. Suggested Technical Interview Questions
6. Suggested Behavioral Interview Questions
7. Screening Recommendation

Keep it concise, professional, and suitable for a Talent Acquisition POC.
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
        return response.json().get("response", "No response received from Ollama.")

    except Exception as e:
        return f"Error connecting to Ollama: {e}"
    
    # -------------------------------------------------------
# Text To Speech
# -------------------------------------------------------
def speak_question(text):

    try:
        tts = gTTS(
            text=text,
            lang="en"
        )

        temp_file = tempfile.NamedTemporaryFile(
            delete=False,
            suffix=".mp3"
        )

        tts.save(temp_file.name)

        return temp_file.name

    except Exception as e:
        st.error(f"TTS Error: {e}")
        return None


# -------------------------------------------------------
# Helper Function: Extract Text From PDF
# -------------------------------------------------------
def extract_pdf_text(uploaded_file):
    pdf = PdfReader(uploaded_file)
    resume_text = ""

    for page in pdf.pages:
        text = page.extract_text()
        if text:
            resume_text += text + "\n"

    return resume_text


# -------------------------------------------------------
# Helper Function: Extract Skills
# -------------------------------------------------------
def extract_skills(text):
    text_lower = text.lower()
    detected_skills = []

    for skill in SKILLS:
        pattern = r"\b" + re.escape(skill.lower()) + r"\b"
        if re.search(pattern, text_lower):
            detected_skills.append(skill)

    return sorted(list(set(detected_skills)))


# -------------------------------------------------------
# Helper Function: Extract Candidate Name
# -------------------------------------------------------
def extract_candidate_name(resume_text):
    lines = resume_text.split("\n")

    for line in lines:
        clean_line = line.strip()
        if clean_line and len(clean_line) > 2:
            return clean_line

    return "Not Found"


# -------------------------------------------------------
# Helper Function: Extract Experience
# -------------------------------------------------------
def extract_experience(resume_text):
    text_lower = resume_text.lower()

    patterns = [
        r"(\d+)\s*\+?\s*years",
        r"over\s+(\d+)\s*\+?\s*years",
        r"(\d+)\s*\+?\s*yrs"
    ]

    for pattern in patterns:
        match = re.search(pattern, text_lower)
        if match:
            return match.group(0)

    return "Not Found"


# -------------------------------------------------------
# Application Header
# -------------------------------------------------------
st.title("🚀 TalentCopilot AI")
st.caption(
    "AI-Powered Talent Intelligence Platform"
)

st.write(
    "Upload a resume, paste a job description, calculate match score, "
    "and generate an AI-assisted recruiter assessment using Ollama."
)

# -------------------------------------------------------
# File Upload and JD Input
# -------------------------------------------------------
uploaded_file = st.file_uploader(
    "Upload Resume",
    type=["pdf"]
)

job_description = st.text_area(
    "Paste Job Description",
    height=250,
    placeholder="Paste the DevOps / Cloud / Platform Engineering job description here..."
)

# -------------------------------------------------------
# Main Processing Logic
# -------------------------------------------------------
if uploaded_file:

    resume_text = extract_pdf_text(uploaded_file)
    resume_lower = resume_text.lower()

    candidate_name = extract_candidate_name(resume_text)
    experience = extract_experience(resume_text)
    resume_skills = extract_skills(resume_text)

    st.success("Resume Uploaded Successfully")

    # ---------------------------------------------------
    # Candidate Summary
    # ---------------------------------------------------
    st.subheader("Candidate Summary")

    col1, col2, col3 = st.columns(3)

    with col1:
        st.metric("Candidate", candidate_name)

    with col2:
        st.metric("Experience", experience)

    with col3:
        st.metric("Skills Found", len(resume_skills))

    # ---------------------------------------------------
    # Skills Found
    # ---------------------------------------------------
    st.subheader("Skills Found in Resume")

    if resume_skills:
        st.write(", ".join(resume_skills))
    else:
        st.warning("No predefined skills detected in the resume.")

    # ---------------------------------------------------
    # Resume Text Preview
    # ---------------------------------------------------
    with st.expander("View Extracted Resume Text"):
        st.text_area(
            "Extracted Text",
            resume_text,
            height=350
        )

    # ---------------------------------------------------
    # JD Match Analysis
    # ---------------------------------------------------
    if job_description:

        jd_skills = extract_skills(job_description)

        matched = sorted(list(set(resume_skills) & set(jd_skills)))
        missing = sorted(list(set(jd_skills) - set(resume_skills)))

        if len(jd_skills) > 0:
            score = round((len(matched) / len(jd_skills)) * 100)
        else:
            score = 0

        st.subheader("Match Analysis")

        col1, col2, col3, col4 = st.columns(4)

        with col1:
            st.metric("Match Score", f"{score}%")

        with col2:
            st.metric("JD Skills", len(jd_skills))

        with col3:
            st.metric("Matched Skills", len(matched))

        with col4:
            st.metric("Missing Skills", len(missing))

        # -----------------------------------------------
        # Pie Chart
        # -----------------------------------------------
        chart_data = {
            "Category": ["Matched", "Missing"],
            "Count": [len(matched), len(missing)]
        }

        fig = px.pie(
            chart_data,
            values="Count",
            names="Category",
            title="Skill Match Overview"
        )

        st.plotly_chart(fig, use_container_width=True)

        # -----------------------------------------------
        # Matched and Missing Skills
        # -----------------------------------------------
        col_left, col_right = st.columns(2)

        with col_left:
            st.subheader("✅ Matched Skills")
            if matched:
                st.write(", ".join(matched))
            else:
                st.warning("No matching skills found.")

        with col_right:
            st.subheader("❌ Missing Skills")
            if missing:
                st.write(", ".join(missing))
            else:
                st.success("No missing skills detected from the JD skill list.")

        # -----------------------------------------------
        # Rule-Based Recommendation
        # -----------------------------------------------
        st.subheader("Hiring Recommendation")

        if score >= 85:
            recommendation = "Strong Match"
            st.success("Strong Match — proceed with technical interview.")
        elif score >= 70:
            recommendation = "Suitable for Interview"
            st.success("Suitable for Interview — candidate meets many key requirements.")
        elif score >= 50:
            recommendation = "Needs Further Review"
            st.warning("Needs Further Review — candidate has partial alignment.")
        else:
            recommendation = "Low Match"
            st.error("Low Match — candidate may not align well with this JD.")

        # -----------------------------------------------
        # Suggested Interview Questions
        # -----------------------------------------------
        st.subheader("Suggested Interview Questions")

        question_bank = {
            "kubernetes": "How would you troubleshoot a pod in CrashLoopBackOff state?",
            "terraform": "How do you manage Terraform remote state securely?",
            "aws": "Explain the difference between IAM users, groups, roles, and policies.",
            "gcp": "How have you used GCP for production workloads?",
            "jenkins": "How do you design and secure a Jenkins CI/CD pipeline?",
            "docker": "What is the difference between a Docker image and a container?",
            "python": "How have you used Python for DevOps automation?",
            "ansible": "How do you structure Ansible playbooks for reusable automation?",
            "prometheus": "How does Prometheus collect metrics from Kubernetes workloads?",
            "grafana": "How do you design Grafana dashboards for production monitoring?",
            "devsecops": "How do you integrate security scanning into CI/CD pipelines?",
            "trivy": "How do you use Trivy for container image vulnerability scanning?",
            "sonarqube": "How do you enforce quality gates using SonarQube?",
            "nexus": "How do you manage artifacts using Nexus Repository Manager?",
            "eks": "What are the key components of an Amazon EKS architecture?",
            "splunk": "How do you use Splunk for application and infrastructure monitoring?",
            "linux": "How would you troubleshoot high CPU or memory usage on a Linux server?"
        }

        generated_questions = []

        for skill in matched:
            if skill in question_bank:
                generated_questions.append(question_bank[skill])

        if generated_questions:
            for idx, question in enumerate(generated_questions[:8], start=1):
                st.write(f"{idx}. {question}")
        else:
            st.info("No predefined interview questions available for the matched skills.")

        # -----------------------------------------------
        # AI Recruiter Assessment Using Ollama
        # -----------------------------------------------
        st.subheader("🤖 AI Recruiter Assessment")

        st.info(
            "This assessment is generated by the local Ollama model "
            "`gemma:2b` and should be used only as screening support."
        )

        if st.button("Generate AI Assessment"):

            with st.spinner("Generating AI assessment using Ollama Gemma 2B..."):

                ai_result = generate_ai_assessment(
                    resume_text,
                    job_description,
                    score,
                    matched,
                    missing
                )

            st.markdown(ai_result)

    else:
        st.info("Paste a Job Description to calculate match score and generate AI assessment.")

else:
    st.info("Upload a PDF resume to begin screening.")

# ---------------------------------------------------
# AI Technical Interview
# ---------------------------------------------------
if uploaded_file and job_description:

    st.divider()
    st.subheader("🎤 AI Technical Interview")

    if st.button("Start AI Interview"):
        st.session_state["start_interview"] = True

    if st.session_state.get("start_interview", False):

        questions = generate_questions(
            resume_text,
            job_description
        )

        responses = []

        for idx, question in enumerate(questions):

            st.markdown(f"### Question {idx + 1}")

            st.write(question)

            audio_file = speak_question(question)

            st.write("Generated audio:", audio_file)

            if audio_file:
                st.audio(audio_file)

            answer = st.text_area(
                "Candidate Answer",
                key=f"answer_{idx}"
            )

            audio_bytes = audio_recorder(                
                text="🎤 Record Answer",
                pause_threshold=10.0,
                sample_rate=41000,
                key=f"audio_{idx}"
            )

            if audio_bytes:

                import os

                os.makedirs("recordings", exist_ok=True)

                with open(
                    f"recordings/question_{idx}.wav",
                    "wb"
                ) as f:

                    f.write(audio_bytes)

                st.success(
                    f"Recording saved: recordings/question_{idx}.wav"
                )

                st.info("Converting speech to text...")

                transcribed_text = transcribe_audio(
                    f"recordings/question_{idx}.wav"
                )

                st.success("Speech converted successfully!")

                st.text_area(
                    "Transcribed Answer",
                    value=transcribed_text,
                    height=150,
                    key=f"transcribed_{idx}"
                )

                answer = transcribed_text

            responses.append({
                "question": question,
                "answer": answer
            })

            col1, col2 = st.columns(2)

            with col1:
                if st.button(
                    f"Expected Answer {idx}"
                ):
                    result = generate_expected_answer(
                        question
                    )
                    st.info(result)

            with col2:
                if answer:
                    if st.button(
                        f"Follow-up Question {idx}"
                    ):
                        followup = generate_followup_question(
                            question,
                            answer
                        )
                        st.success(followup)

    if st.button(
        "Generate Interview Report"
    ):

        with st.spinner(
            "Generating interview report..."
        ):

            report = generate_interview_report(
                responses
            )

        st.subheader(
            "📄 Interview Evaluation"
        )

        st.markdown(report)