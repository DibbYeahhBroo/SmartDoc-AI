import streamlit as st
from PyPDF2 import PdfReader
from transformers import pipeline

@st.cache_resource
def load_summarizer():
    return pipeline("summarization", model="sshleifer/distilbart-cnn-12-6")

summarizer = load_summarizer()

st.subheader("Upload a PDF file")
uploaded_file = st.file_uploader(" ", type="pdf")

if uploaded_file is not None:
    reader = PdfReader(uploaded_file)
    text = ""

    for page in reader.pages:
        text += page.extract_text() or ""

    st.subheader("Extracted Text")
    st.text_area("Text from PDF", text, height=400)

if st.button("Summarize Text"):
    if len(text.strip()) == 0:
        st.warning("No text found to summarize.")
    else:
        st.info("Summarizing, please wait...")
        max_chunk = 2000
        text_chunks = [text[i:i+max_chunk] for i in range(0, len(text), max_chunk)]
        summary = ""

        for i, chunk in enumerate(text_chunks):
            #st.write(f"Summarizing chunk {i+1}/{len(text_chunks)}...")
            try:
                result = summarizer(chunk, max_length=200, min_length=50, do_sample=False)
                summarized = result[0]['summary_text']
                summary += summarized + " "
            except Exception as e:
                st.error(f"Error summarizing chunk {i+1}: {e}")

        st.subheader("Summary")
        st.text_area("Summarized Text", summary.strip(), height=500)