import streamlit as st
from resume_analysis import analyze_resume

# Page title
st.title("AI-Powered Resume Reviewer")

# File uploader for resume
uploaded_file = st.file_uploader("Upload Your Resume (Text, PDF, or Word File)", type=["txt", "pdf", "docx"])

# Text area for job description
job_description = st.text_area("Enter Job Description")

if uploaded_file is not None and job_description:
    # Check the file type and extract text
    file_type = uploaded_file.name.split(".")[-1].lower()
    resume_text = None

    try:
        if file_type == "txt":
            resume_text = uploaded_file.read().decode("utf-8")
        elif file_type == "pdf":
            from PyPDF2 import PdfReader
            reader = PdfReader(uploaded_file)
            resume_text = "".join(page.extract_text() for page in reader.pages)
        elif file_type == "docx":
            from docx import Document
            doc = Document(uploaded_file)
            resume_text = "\n".join(para.text for para in doc.paragraphs)
        else:
            st.error("Unsupported file type.")
    except Exception as e:
        st.error(f"Error processing file: {e}")

    if resume_text:
        # Analyze the resume
        results = analyze_resume(resume_text, job_description)

        # Display parsed resume sections
        st.subheader("Parsed Resume Sections")
        for section, content in results["parsed_resume"].items():
            with st.expander(section.capitalize()):
                st.write(content if content else "Not Found")

        # Display analysis results
        st.subheader("Analysis Results")
        st.write(f"**Match Score:** {results['match_score']:.2f}%")
        
        # Safe access to the 'grammar_errors' key using .get()
        grammar_errors = results.get("grammar_errors", None)
        st.write("**Grammar Errors:**")
        if grammar_errors:
            st.write(grammar_errors)
        else:
            st.write("No grammar errors detected.")

        st.write("**Job Summary:**", results["job_summary"])
        # st.write("**Keyword Matches:**", results["keyword_matches"] if results["keyword_matches"] else "No matches found.")

        # Display "Fit for Job" conclusion
        st.subheader("Fit for the Job:")
        if results["fit_for_job"]:
            st.success("The candidate is a good fit for the job!")
        else:
            st.error("The candidate is not a good fit for the job.")
    else:
        st.error("Could not extract text from the uploaded file. Please try again with a supported format.")
else:
    st.write("Please upload a resume and enter a job description to proceed.")
