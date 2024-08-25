import base64
import os
import io
from PIL import Image
import fitz  # PyMuPDF
import google.generativeai as genai
import streamlit as st
from dotenv import load_dotenv

load_dotenv()

# Configure the generative AI model
genai.configure(api_key=os.getenv('GOOGLE_API_KEY'))

# Define functions for processing and generating content
def geminiResponse(input, pdfContent, prompt):
    model = genai.GenerativeModel('gemini-1.5-flash')
    response = model.generate_content([input, pdfContent, prompt])
    return response.text

def inputPdf(uploaded_file):
    if uploaded_file is not None:
        pdf_document = fitz.open(stream=uploaded_file.read(), filetype="pdf")
        images = []

        # Loop through all pages and render them as images
        for page_number in range(len(pdf_document)):
            page = pdf_document.load_page(page_number)  # Get the page
            pix = page.get_pixmap()  # Render page to an image
            img = Image.open(io.BytesIO(pix.tobytes("png")))  # Save as PNG for better compatibility
            images.append(img)

        # Combine images into a single image
        widths, heights = zip(*(img.size for img in images))
        total_height = sum(heights)
        max_width = max(widths)

        combined_image = Image.new('RGB', (max_width, total_height))

        y_offset = 0
        for img in images:
            combined_image.paste(img, (0, y_offset))
            y_offset += img.height

        # Convert combined image to bytes
        img_byt_arr = io.BytesIO()
        combined_image.save(img_byt_arr, format="JPEG")
        img_byt_arr = img_byt_arr.getvalue()

        pdf_part = {
            "mime_type": "image/jpeg",
            "data": base64.b64encode(img_byt_arr).decode()
        }

        return pdf_part
    else:
        raise FileNotFoundError("No File Uploaded")

# Set the page configuration
st.set_page_config(page_title="ATS Checker", page_icon="📝", layout="centered")

# Add a title and description
st.title("ATS Resume Checker")
st.write("""
    Upload your resume and compare it against a job description to see how well it matches. 
    Get insights on strengths, weaknesses, and an ATS compatibility score.
""")

# Job description input
input_text = st.text_area("Job Description", placeholder="Paste the job description here...")

# Resume upload
uploaded_files = st.file_uploader("Upload Your Resume (PDF)", type=["pdf"])

if uploaded_files is not None:
    st.success("Resume uploaded successfully!")

# Action buttons
col1, col2 = st.columns(2)
with col1:
    submit1 = st.button("Analyze Resume")
with col2:
    submit3 = st.button("Get ATS Score")

# Define input prompts
input_Prompt1 = (
    "You are an ATS (Application Tracking System) with deep functionality. Analyze the provided resume for its match with the specified job description by calculating a percentage match and identifying key strengths and weaknesses. "
    "Highlight areas where the candidate aligns well with the job requirements and pinpoint any gaps or misalignments. Provide actionable suggestions for improvement, "
    "such as adding relevant keywords, refining content, or addressing skill deficiencies. Ensure the feedback is clear and concise, helping the candidate enhance their resume's relevance and increase their chances of success."
)

input_Prompt2 = (
    "Calculate the ATS compatibility percentage for the provided resume against the job description for [Job Title]. "
    "Evaluate how closely the resume matches the job requirements based on keywords, skills, experience, and education."
)

# Handle button actions
if submit1:
    if uploaded_files is not None:
        pdf_content = inputPdf(uploaded_files)
        response = geminiResponse(input_Prompt1, pdf_content, input_text)
        st.subheader("Resume Analysis")
        st.write(response)
    else:
        st.error("Please upload your resume to analyze.")

elif submit3:
    if uploaded_files is not None:
        pdf_content = inputPdf(uploaded_files)
        response = geminiResponse(input_Prompt2, pdf_content, input_text)
        st.subheader("ATS Compatibility Score")
        st.write(response)
    else:
        st.error("Please upload your resume to get the ATS score.")

# Footer
st.markdown("---")
st.markdown("Powered by [Gemini AI](https://ai.google/generative-ai)")
st.markdown("Developed with ❤️ using [Streamlit](https://streamlit.io/)")

