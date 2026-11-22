import streamlit as st
import pymupdf
import re
import pandas as pd

# Load Skill Library

with open("skills.txt", "r", encoding="utf-8") as file:
    all_skills = [
        line.strip()
        for line in file
        if line.strip()
    ]


# PDF Text Extraction

def extract_resume_text(uploaded_file):

    pdf_bytes = uploaded_file.read()

    doc = pymupdf.open(
        stream=pdf_bytes,
        filetype="pdf"
    )

    text = ""

    for page in doc:
        text += page.get_text()

    return text


# Resume Cleaning

def clean_resume(text):

    text = text.lower()

    text = text.replace("\n", " ")

    text = re.sub(
        r"[^a-z0-9\s]",
        " ",
        text
    )

    text = " ".join(text.split())

    return text


# Skill Extraction

def extract_skills(text, skills):

    text = text.lower()

    found = []

    for skill in skills:

        pattern = r'\b' + re.escape(skill.lower()) + r'\b'

        if re.search(pattern, text):
            found.append(skill)

    return found

# UI

st.set_page_config(
    page_title="AI Resume Ranker",
    page_icon="📄",
    layout="wide"
)

st.title("📄 AI Resume Ranker")

st.markdown("""
Upload one or more resumes and compare them against a job description.
The system extracts skills, calculates a match score, ranks candidates,
and provides recommendations.
""")

uploaded_resumes = st.file_uploader(
    "Upload Resume PDFs",
    type=["pdf"],
    accept_multiple_files=True
)

job_description = st.text_area(
    "Paste Job Description"
)

# Analyze Button

if st.button("Analyze Resumes"):

    if uploaded_resumes and job_description:

        results = []

        jd_skills = extract_skills(
            job_description,
            all_skills
        )

        if not jd_skills:
            st.error(
                "No recognizable skills found in the Job Description."
            )
            st.stop()

        for uploaded_resume in uploaded_resumes:

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
            )

            results.append({
                "Resume": uploaded_resume.name,
                "Score": score,
                "Matched": matched,
                "Missing": missing,
                "Skills": resume_skills
            })

        # Ranking

        results.sort(
            key=lambda x: x["Score"],
            reverse=True
        )

        top_candidate = results[0]

        st.success(
            f"🏆 Best Candidate: "
            f"{top_candidate['Resume']} "
            f"({top_candidate['Score']:.2f}%)"
        )

        # Leaderboard

        leaderboard = pd.DataFrame([
            {
                "Rank": i + 1,
                "Resume": r["Resume"],
                "Score (%)": round(
                    r["Score"],
                    2
                )
            }
            for i, r in enumerate(results)
        ])

        st.subheader("🏆 Candidate Leaderboard")

        st.dataframe(
            leaderboard,
            use_container_width=True
        )

        # Resume Details

        st.header("Detailed Analysis")

        for rank, result in enumerate(results, start=1):

            with st.expander(
                f"#{rank} - {result['Resume']} "
                f"({result['Score']:.2f}%)"
            ):

                st.metric(
                    "Resume Match Score",
                    f"{result['Score']:.2f}%"
                )

                st.progress(
                    min(
                        result["Score"] / 100,
                        1.0
                    )
                )

                col1, col2 = st.columns(2)

                with col1:

                    st.subheader(
                        "✅ Matched Skills"
                    )

                    for skill in sorted(
                        result["Matched"]
                    ):
                        st.write(
                            f"• {skill}"
                        )

                with col2:

                    st.subheader(
                        "❌ Missing Skills"
                    )

                    for skill in sorted(
                        result["Missing"]
                    ):
                        st.write(
                            f"• {skill}"
                        )

                st.subheader(
                    "📋 Skills Detected In Resume"
                )

                for skill in sorted(
                    result["Skills"]
                ):
                    st.write(
                        f"✅ {skill}"
                    )

                st.subheader(
                    "💡 Recommendation"
                )

                if result["Missing"]:

                    st.info(
                        "Consider learning: "
                        + ", ".join(
                            sorted(
                                result["Missing"]
                            )
                        )
                    )

                else:

                    st.success(
                        "Excellent match for the role!"
                    )

    else:

        st.warning(
            "Please upload resumes and enter a Job Description."
        )
