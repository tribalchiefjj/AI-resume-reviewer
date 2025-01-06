import spacy
from transformers import pipeline
import re

# Load spaCy model
nlp = spacy.load("en_core_web_sm")

# Load NLP model from Hugging Face
summarizer = pipeline("summarization")

def parse_resume(resume_text):
    """
    Parse resume text to extract key sections like Experience, Education, and Skills.
    """
    section_patterns = {
        "Experience": r"(experience|work history|employment history):?",
        "Education": r"(education|academic background):?",
        "Skills": r"(skills|technical skills|expertise):?",
    }

    parsed_sections = {key: "" for key in section_patterns}

    lines = resume_text.split("\n")
    current_section = None
    for line in lines:
        line = line.strip().lower()
        for section, pattern in section_patterns.items():
            if re.match(pattern, line):
                current_section = section
                break
        if current_section:
            parsed_sections[current_section] += line + "\n"

    for section in parsed_sections:
        parsed_sections[section] = parsed_sections[section].strip()

    return parsed_sections

def analyze_resume(resume_text, job_description):
    """
    Analyzes the resume text against the job description and returns analysis results, including fit for job.
    """
    # Parse the resume
    parsed_resume = parse_resume(resume_text)

    # Summarize the job description
    job_summary = summarizer(job_description, max_length=50, min_length=25, do_sample=False)

    # Keyword matching
    keywords = job_description.split()
    matches = [word for word in keywords if word in resume_text]

    # Fit for job determination
    fit_for_job = False
    match_score = len(matches) / len(keywords) * 100
    if match_score >= 70:  # You can adjust this threshold based on your criteria
        fit_for_job = True

    return {
        "parsed_resume": parsed_resume,
        "job_summary": job_summary[0]["summary_text"],
        # "keyword_matches": matches,
        "match_score": match_score,
        "fit_for_job": fit_for_job,  # Return fit for job status
    }

def extract_experience(resume_text):
    """
    Extracts the work experience from the resume text.
    
    :param resume_text: The content of the resume.
    :return: A list of dictionaries containing job titles, companies, and dates.
    """
    experience_section = ""
    experience_pattern = r"(experience|work history|employment history):?([\s\S]*?)(education|skills|awards|$)"
    match = re.search(experience_pattern, resume_text, re.IGNORECASE)

    if match:
        experience_section = match.group(2)

    # Extract job title, company, and date
    experience_entries = []
    job_pattern = r"(?P<title>[\w\s]+(?:\s+[\w\s]+)?)\s*at\s*(?P<company>[\w\s]+(?:\s+[\w\s]+)?)\s*(?:\(|\b)(?P<dates>[\d]{4}-[\d]{4}|\d{4}|\d{4}-Present)?(?:\)|\b)"
    job_matches = re.findall(job_pattern, experience_section)

    for job in job_matches:
        experience_entries.append({
            "title": job[0].strip(),
            "company": job[1].strip(),
            "dates": job[2].strip() if job[2] else "Not specified"
        })

    return experience_entries

