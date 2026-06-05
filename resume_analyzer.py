import os
from openai import OpenAI

# Setup Groq
os.environ["GROQ_API_KEY"] = "YOUR_GROQ_KEY_HERE"

client = OpenAI(
    base_url="https://api.groq.com/openai/v1",
    api_key=os.environ["GROQ_API_KEY"]
)

def extract_skills(resume_text):
    """Extract skills from resume text using AI"""
    prompt = f"""
    Extract all technical and professional skills from this resume.
    Return only a Python list of skills, nothing else.
    
    Resume text:
    {resume_text[:2000]}  # First 2000 characters
    """
    
    response = client.chat.completions.create(
        model="llama-3.1-8b-instant",
        messages=[{"role": "user", "content": prompt}]
    )
    
    return response.choices[0].message.content

# Test with a sample resume
sample_resume = """
Experienced software developer with 5 years in Python and JavaScript.
Worked with Django, React, and PostgreSQL.
Familiar with AWS, Docker, and Git.
"""

skills = extract_skills(sample_resume)
print("Extracted skills:", skills)
