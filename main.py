import streamlit as st
import PyPDF2
import io
import os
import google.generativeai as genai

st.set_page_config(page_title="AI Resume Reviewer", page_icon="📃", layout="centered")

st.title("AI Resume Reviewer")
st.markdown("Upload your resume and get AI-powered feedback tailored to your needs!")

# Api key from sectrets of streamlit
GEMINI_API_KEY = st.secrets["GEMINI_API_KEY"]
st.success("API key loaded!")  # Debug message
genai.configure(api_key=GEMINI_API_KEY)

uploaded_file = st.file_uploader("Upload your Resume(PDF or TXT)", type=["pdf", "txt"])
job_role = st.text_input("Enter the job role you are targetting (optional)")

analyze = st.button("Analyze Resume")


# function to extract text from pdf
def extract_text_from_pdf(pdf_file):
    pdf_reader = PyPDF2.PdfReader(pdf_file)
    text = ""
    for page in pdf_reader.pages:
        text += page.extract_text() + "\n"
    return text


# function to extract the content form file if it is a pdf or text file.
def extract_text_from_file(uploaded_file):
    if uploaded_file.type == "application/pdf":
        return extract_text_from_pdf(io.BytesIO(uploaded_file.read()))
    return uploaded_file.read().decode("utf-8")


# When we upload the file and click the button
if analyze and uploaded_file:
    try:
        file_content = extract_text_from_file(uploaded_file)  # from this line we get the content of the file

        if not file_content.strip():
            st.error("file does not have any content...")
            st.stop()

        st.write(f"Content length: {len(file_content)} characters")  # Debug: content length

        prompt = f"""Please analyze this resume and provide constructive feedback.
        Focus on the following aspects:
        1. Content clarity and impact
        2. Skills presentation
        3. Experience descriptions
        4. Specific improvement for {job_role if job_role else 'general job appplication'}

        Resume content:
        {file_content}

        Please provide your analysis in a clear, structured format with specific recommendations."""

        # Gemini API call with spinner and config
        with st.spinner("Analyzing resume..."):
            model = genai.GenerativeModel("gemini-1.5-flash")  # or "gemini-1.5-pro" for higher quality
            response = model.generate_content(prompt, generation_config={"max_output_tokens": 1024})

        st.markdown("### Analysis Results")
        st.markdown(response.text)

    except Exception as e:
        st.error(f"An error occured: {str(e)}")
