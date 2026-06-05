import os
from openai import OpenAI
import PyPDF2

os.environ["GROQ_API_KEY"] = "YOUR_GROQ_KEY_HERE"

client = OpenAI(
    base_url="https://api.groq.com/openai/v1",
    api_key=os.environ["GROQ_API_KEY"]
)

def read_pdf(file_path):
    with open(file_path, 'rb') as file:
        pdf_reader = PyPDF2.PdfReader(file)
        text = ""
        for page in pdf_reader.pages:
            text += page.extract_text()
    return text

def extract_skills(resume_text):
    prompt = f"""
    Extract all technical and professional skills from this resume.
    Return only a Python list of skills, nothing else.
    
    Resume text:
    {resume_text[:2000]}
    """
    
    response = client.chat.completions.create(
        model="llama-3.1-8b-instant",
        messages=[{"role": "user", "content": prompt}]
    )
    
    return eval(response.choices[0].message.content)

# Read from PDF
print("Reading from sample_resume.pdf...")
resume_text = read_pdf("sample_resume.pdf")
skills = extract_skills(resume_text)

print(f"\nExtracted skills from PDF: {skills}")
