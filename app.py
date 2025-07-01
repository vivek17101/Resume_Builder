import streamlit as st
import requests
import os
import fitz  # PyMuPDF
from io import BytesIO
from docx import Document
from dotenv import load_dotenv

# Load .env file
load_dotenv()
OPENROUTER_API_KEY = os.getenv("OPENROUTER_API_KEY")

# ✅ Use the newer Mistral 24B model (free for now)
MODEL = "mistralai/mistral-small-3.2-24b-instruct"
OPENROUTER_API_URL = "https://openrouter.ai/api/v1/chat/completions"

st.set_page_config(page_title="Free AI Resume Enhancer", layout="centered")
st.title("📄 Free AI Resume Enhancer (Powered by OpenRouter)")

st.markdown("""
Enhance your resume using AI — completely free!  
This tool will:
- Improve professionalism and clarity  
- Optimize for Applicant Tracking Systems (ATS)  
- Maintain your original content while enhancing presentation  
""")

with st.expander("ℹ️ How to use this tool"):
    st.write("""
    1. Upload a PDF or paste your resume text  
    2. AI will rewrite it in a more professional and optimized format  
    3. Download your improved resume in `.txt` or `.docx` format  
    """)

# Upload resume
st.subheader("1. Upload your resume (PDF)")
uploaded_file = st.file_uploader("Choose a PDF file", type="pdf")

resume_text = ""
if uploaded_file is not None:
    try:
        with fitz.open(stream=uploaded_file.read(), filetype="pdf") as doc:
            resume_text = "\n".join(page.get_text() for page in doc)
        st.success("✓ PDF successfully read!")
    except Exception as e:
        st.error(f"Failed to read PDF: {e}")

# Paste resume content manually
st.subheader("2. Review or edit your resume content")
text_input = st.text_area("Resume Content", resume_text, height=300)

# Check for API key early
if not OPENROUTER_API_KEY:
    st.error("API key not found! Please check your .env file or Streamlit secrets.")

def enhance_resume_with_openrouter(text):
    """Send resume to OpenRouter LLM for enhancement"""
    headers = {
        "Authorization": f"Bearer {OPENROUTER_API_KEY}",
        "Content-Type": "application/json",
        "HTTP-Referer": "http://localhost"  # Replace if hosted (e.g., https://yourapp.streamlit.app)
    }

    prompt = f"""
You are a professional resume writer. Rewrite the resume text below to be:
- More professional and concise
- Optimized for Applicant Tracking Systems (ATS)
- Easy to scan for recruiters
- Maintain original section structure and facts

ONLY return the enhanced resume content.

Original Resume:
{text}
"""

    body = {
    "model": MODEL,
    "messages": [
        {
            "role": "system",
            "content": (
                "You are a professional resume writer with deep knowledge of ATS systems and modern hiring trends. "
                "Your job is to rewrite resumes to sound clear, professional, and tailored for job applications, "
                "while preserving original meaning and section structure."
            )
        },
        {
            "role": "user",
            "content": prompt
        }
    ]
}


    try:
        response = requests.post(OPENROUTER_API_URL, headers=headers, json=body)
        response.raise_for_status()
        result = response.json()
        return result["choices"][0]["message"]["content"].strip()

    except Exception as e:
        st.error(f"Error during API call: {e}")
        return None

# Enhance resume
if st.button("✨ Enhance My Resume"):
    content = text_input.strip()
    if not content:
        st.warning("Please provide resume content.")
    else:
        with st.spinner("Enhancing resume with OpenRouter AI..."):
            enhanced_resume = enhance_resume_with_openrouter(content)

            if enhanced_resume:
                st.success("✅ Resume enhanced successfully!")
                st.subheader("3. Your Enhanced Resume")
                st.text_area("Enhanced Resume", value=enhanced_resume, height=400)

                st.subheader("4. Download Options")
                col1, col2 = st.columns(2)

                with col1:
                    st.download_button(
                        "📝 Download as .txt",
                        data=BytesIO(enhanced_resume.encode()),
                        file_name="enhanced_resume.txt",
                        mime="text/plain"
                    )
                with col2:
                    doc = Document()
                    doc.add_paragraph(enhanced_resume)
                    doc_io = BytesIO()
                    doc.save(doc_io)
                    doc_io.seek(0)
                    st.download_button(
                        "💾 Download as .docx",
                        data=doc_io,
                        file_name="enhanced_resume.docx",
                        mime="application/vnd.openxmlformats-officedocument.wordprocessingml.document"
                    )

# Reset
st.markdown("---")
if st.button("🔄 Start Over"):
    st.rerun()

st.caption("Powered by OpenRouter.ai — Use your free API key from [https://openrouter.ai](https://openrouter.ai)")
