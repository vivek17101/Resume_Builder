import streamlit as st
import requests
import os
import fitz  # PyMuPDF
from io import BytesIO
from docx import Document
from dotenv import load_dotenv

# Load .env file for local development.
# In Streamlit Cloud, prefer using st.secrets for API keys.
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
    1. Upload a PDF or paste your resume text.
    2. (Optional) Provide a job description to tailor the enhancement.
    3. AI will rewrite it in a more professional and optimized format.
    4. Download your improved resume in `.txt` or `.docx` format.
    """)

# --- Section 1: Upload or Paste Resume ---
st.subheader("1. Upload your resume (PDF) or paste content")
uploaded_file = st.file_uploader("Choose a PDF file", type="pdf")

resume_text_from_pdf = ""
if uploaded_file is not None:
    try:
        with fitz.open(stream=uploaded_file.read(), filetype="pdf") as doc:
            resume_text_from_pdf = "\n".join(page.get_text() for page in doc)
        st.success("✓ PDF successfully read!")
    except Exception as e:
        st.error(f"Failed to read PDF: {e}")

# Provide example text if no PDF is uploaded and text_input is empty
example_resume_text = """
John Doe
123 Main St, Anytown, USA | (123) 456-7890 | john.doe@email.com

Summary
Motivated individual seeking opportunities. Has experience in customer service.

Experience
Customer Service Rep | ABC Company | 2020-Present
- Answered phones
- Helped customers

Education
High School Diploma | Anytown High | 2020
"""

# Use session state to manage the text area content
if "resume_input_text" not in st.session_state:
    st.session_state.resume_input_text = resume_text_from_pdf if resume_text_from_pdf else example_resume_text
elif resume_text_from_pdf and st.session_state.resume_input_text == example_resume_text:
    # If a PDF is newly uploaded, replace example text with PDF content
    st.session_state.resume_input_text = resume_text_from_pdf

text_input = st.text_area(
    "Resume Content (edit as needed)",
    value=st.session_state.resume_input_text,
    height=300,
    key="resume_text_area" # Add a key for the text area
)

# Clear input button
if st.button("Clear Resume Content", help="Clears the text area"):
    st.session_state.resume_input_text = ""
    st.rerun() # Rerun to clear the text area immediately

# --- Section 2: Optional Job Description ---
st.subheader("2. (Optional) Provide a Job Description")
job_description_input = st.text_area(
    "Paste the Job Description here (for tailored enhancement)",
    height=150,
    placeholder="e.g., 'Seeking a highly motivated Software Engineer with experience in Python and cloud platforms...'"
)

# Check for API key early
if not OPENROUTER_API_KEY:
    st.error("API key not found! Please set `OPENROUTER_API_KEY` in your `.env` file (for local) or Streamlit secrets (for deployment).")
    st.info("For Streamlit Cloud deployments, use `st.secrets` by adding `OPENROUTER_API_KEY = 'your_key_here'` to `.streamlit/secrets.toml`.")

def enhance_resume_with_openrouter(resume_content, job_description=None):
    """
    Sends resume content to OpenRouter LLM for enhancement,
    optionally tailoring it with a job description.
    """
    headers = {
        "Authorization": f"Bearer {OPENROUTER_API_KEY}",
        "Content-Type": "application/json",
        "HTTP-Referer": "http://localhost"  # Replace if hosted (e.g., https://your_app_name.streamlit.app)
    }

    # IMPORTANT: Added instruction to avoid Markdown formatting
    system_message_content = (
        "You are a professional resume writer with deep knowledge of ATS systems and modern hiring trends. "
        "Your job is to rewrite resumes to sound clear, professional, and tailored for job applications, "
        "while preserving original meaning and section structure. "
        "Crucially, DO NOT invent new information or skills not present in the original resume. "
        "Focus on rephrasing, optimizing keywords, and improving readability. "
        "**IMPORTANT: Do NOT use any Markdown formatting (like bolding with **, italics with *, or numbered lists). Return plain text only.**"
    )

    # IMPORTANT: Added instruction to avoid Markdown formatting in the user prompt as well
    user_prompt = f"""
Rewrite the resume text below to be:
- More professional and concise
- Optimized for Applicant Tracking Systems (ATS)
- Easy to scan for recruiters
- Maintain original section structure and facts
- DO NOT invent new information or skills.
- **Ensure the output is pure plain text, without any Markdown formatting.**

Original Resume:
{resume_content}
"""

    body = {
        "model": MODEL,
        "messages": [
            {
                "role": "system",
                "content": system_message_content
            },
            {
                "role": "user",
                "content": user_prompt
            }
        ]
    }

    try:
        response = requests.post(OPENROUTER_API_URL, headers=headers, json=body)
        response.raise_for_status()  # Raise an HTTPError for bad responses (4xx or 5xx)
        result = response.json()
        if "choices" in result and len(result["choices"]) > 0 and "message" in result["choices"][0]:
            return result["choices"][0]["message"]["content"].strip()
        else:
            st.error("Unexpected response format from OpenRouter API.")
            st.json(result) # Display the full response for debugging
            return None

    except requests.exceptions.HTTPError as http_err:
        st.error(f"HTTP error occurred: {http_err} - Response: {response.text}")
        return None
    except requests.exceptions.ConnectionError as conn_err:
        st.error(f"Connection error occurred: {conn_err} - Check your internet connection or API endpoint.")
        return None
    except requests.exceptions.Timeout as timeout_err:
        st.error(f"Timeout error occurred: {timeout_err} - The request took too long.")
        return None
    except requests.exceptions.RequestException as req_err:
        st.error(f"An unexpected error occurred during the API request: {req_err}")
        return None
    except Exception as e:
        st.error(f"An error occurred while processing the API response: {e}")
        return None

# --- Section 3: Enhance Resume Button ---
if st.button("✨ Enhance My Resume", use_container_width=True):
    content = text_input.strip()
    if not content:
        st.warning("Please provide resume content to enhance.")
    elif not OPENROUTER_API_KEY:
        st.error("API key is missing. Please set it up as instructed above.")
    else:
        with st.spinner("Enhancing resume with OpenRouter AI... This may take a moment."):
            enhanced_resume = enhance_resume_with_openrouter(content, job_description_input.strip())

            if enhanced_resume:
                st.success("✅ Resume enhanced successfully!")
                st.subheader("3. Your Enhanced Resume")
                st.text_area("Enhanced Resume", value=enhanced_resume, height=400, key="enhanced_resume_output")

                st.subheader("4. Download Options")
                col1, col2 = st.columns(2)

                with col1:
                    st.download_button(
                        "📝 Download as .txt",
                        data=BytesIO(enhanced_resume.encode()),
                        file_name="enhanced_resume.txt",
                        mime="text/plain",
                        use_container_width=True
                    )
                with col2:
                    doc = Document()
                    # Split the enhanced resume into paragraphs for better DOCX formatting
                    for paragraph_text in enhanced_resume.split('\n'):
                        if paragraph_text.strip(): # Avoid adding empty paragraphs
                            doc.add_paragraph(paragraph_text)
                    doc_io = BytesIO()
                    doc.save(doc_io)
                    doc_io.seek(0)
                    st.download_button(
                        "💾 Download as .docx",
                        data=doc_io,
                        file_name="enhanced_resume.docx",
                        mime="application/vnd.openxmlformats-officedocument.wordprocessingml.document",
                        use_container_width=True
                    )
            else:
                st.error("Failed to enhance resume. Please check the error messages above.")

# --- Reset Button ---
st.markdown("---")
if st.button("🔄 Start Over", help="Clears all inputs and restarts the app"):
    # Clear session state variables to truly reset
    for key in st.session_state.keys():
        del st.session_state[key]
    st.rerun()

st.caption("Powered by OpenRouter.ai — Use your free API key from [https://openrouter.ai](https://openrouter.ai)")
