import base64

import pdf2image
from dotenv import load_dotenv

load_dotenv()

import streamlit as st
import os as os
import io
from PIL import Image
import pdf2image as pdf
import google.generativeai as genai

genai.configure(api_key=os.getenv(key="GOOGLE_API_KEY"))


def geminiResponse(input, pdfContent, prompt):
    model = genai.GenerativeModel('gemini-1.5-flash')
    response = model.generate_content([input, pdfContent[0], prompt])
    return response.text


def inputPdf(uploaded_file):
    if uploaded_file is not None:
        images = pdf.convert_from_bytes(uploaded_file.read())
        firstPage = images[0]

        # convert to bytes
        img_byt_arr = io.BytesIO()
        firstPage.save(img_byt_arr, format="JPEG")
        img_byt_arr = img_byt_arr.getvalue()

        pdf_parts = [
            {
                "mime_type": "image/jpeg",
                "data": base64.b64encode(img_byt_arr).decode()
            }
        ]
        return pdf_parts
    else:
        raise FileNotFoundError("No File Uploaded")


st.set_page_config(page_title="ATS Checker")
st.header("ATS Tracking")
input_text = st.text_area("Job Description: ", key="input")
uploaded_files = st.file_uploader("Upload your Resume: ", type=["pdf"])
if uploaded_files is not None:
    st.write("File Uploaded")

submit1 = st.button("Tell me about resume")
    # button2 = st.button("How can I improve my skills")
submit3 = st.button("Percentage Match")

input_Prompt1 = (
    " you are ATS (Application Tracking System) with deep ATS functionality Analyze the provided resume for its match with the specified job description by calculating a percentage match and identifying key strengths and weaknesses. "
    "Highlight the areas where the candidate aligns well with the job requirements and pinpoint any gaps or misalignments. Provide actionable suggestions for improvement, "
    "such as adding relevant keywords, refining content, or addressing skill deficiencies. Ensure the feedback is clear and concise,"
    " helping the candidate to enhance their resume's relevance and increase their chances of success.")
input_Prompt2 = (
    "Evaluate the resume against the provided job description and calculate the ATS percentage score. Determine how closely the resume matches the job requirements, considering keywords, skills, experience, and education. "
    "Provide a clear score reflecting the alignment, and briefly indicate key factors that contributed to the score, such as missing keywords or mismatched qualifications.")

if submit1:
    if uploaded_files is not None:
        pdf_content = inputPdf(uploaded_files)
        response = geminiResponse(input_Prompt1, pdf_content, input_text)
        st.subheader("the response is")
        st.write(response)
    else:
        st.write("Please Upload the Resume")

elif submit3:
    if uploaded_files is not None:
        pdft_content = inputPdf(uploaded_files)
        response = geminiResponse(input_Prompt2, pdft_content, input_text)
        st.subheader("The response is: ")
        st.write(response)
    else:
        st.write("Please upload the Resume")
