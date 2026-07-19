import streamlit as st
import PyPDF2
import re

# Load skill library
with open("skills.txt", "r") as file:
    all_skills = [
        line.strip()
        for line in file
        if line.strip()
    ]


# Skill extraction function
def extract_skills(text, skills):

    text = text.lower()

    found = []

    for skill in skills:

        if skill.lower() in text:
            found.append(skill)

    return found


# PDF Extraction
def extract_resume_text(uploaded_file):

    reader = PyPDF2.PdfReader(uploaded_file)

    text = ""

    for page in reader.pages:

        page_text = page.extract_text()

        if page_text:
            text += page_text

    return text


# Text cleaning
def clean_resume(text):

    text = text.lower()

    text = text.replace("\n", " ")

    text = re.sub(r"[^a-z0-9\s]", " ", text)

    text = " ".join(text.split())

    return text


# UI
st.title("📄 AI Resume Ranker")

st.write(
    "Upload a resume and paste a job description to evaluate candidate suitability."
)

uploaded_resume = st.file_uploader(
    "Upload Resume (PDF)",
    type=["pdf"]
)

job_description = st.text_area(
    "Paste Job Description"
)

if st.button("Analyze Resume"):

    if uploaded_resume and job_description:

        resume_text = extract_resume_text(
            uploaded_resume
        )

        clean_text = clean_resume(
            resume_text
        )

        resume_skills = extract_skills(
            clean_text,
            all_skills
        )

        jd_skills = extract_skills(
            job_description,
            all_skills
        )

        matched = list(
            set(resume_skills)
            &
            set(jd_skills)
        )

        missing = list(
            set(jd_skills)
            -
            set(resume_skills)
        )

        score = (
            len(matched)
            /
            len(jd_skills)
            * 100
        ) if jd_skills else 0

        st.success(
            f"Resume Match Score: {score:.2f}%"
        )

        st.subheader("✅ Matched Skills")

        for skill in sorted(matched):
            st.write(skill)

        st.subheader("❌ Missing Skills")

        for skill in sorted(missing):
            st.write(skill)

        st.subheader("💡 Recommendation")

        if missing:

            st.write(
                "Consider learning:"
            )

            for skill in sorted(missing):
                st.write(f"• {skill}")

        else:

            st.success(
                "Excellent match for the role!"
            )

    else:

        st.warning(
            "Upload a resume and enter a job description."
        )