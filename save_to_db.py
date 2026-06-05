import os
from dotenv import load_dotenv
from supabase import create_client
from openai import OpenAI
import PyPDF2

load_dotenv()

# Supabase setup
supabase = create_client(
    os.getenv("SUPABASE_URL"),
    os.getenv("SUPABASE_KEY")
)

# Groq setup
client = OpenAI(
    base_url="https://api.groq.com/openai/v1",
    api_key=os.getenv("GROQ_API_KEY")
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

# Market skills
market_skills = ['Python', 'SQL', 'AWS', 'Docker', 'Kubernetes', 'React', 'Node.js', 'Machine Learning', 'Data Analysis', 'Cybersecurity', 'Terraform', 'Git']

# Process a resume
file_path = "sample_resume.pdf"
print(f"Processing {file_path}...")

resume_text = read_pdf(file_path)
skills = extract_skills(resume_text)

# Find missing skills
your_set = set(s.lower() for s in skills)
market_set = set(s.lower() for s in market_skills)
missing = list(market_set - your_set)

# Save to Supabase
data = {
    "resume_text": resume_text[:1000],
    "extracted_skills": skills,
    "missing_skills": missing,
    "recommendation": "Pending",
    "file_name": file_path
}

result = supabase.table("resume_analyses").insert(data).execute()
print(f"✅ Saved to database! ID: {result.data[0]['id']}")
print(f"📊 Skills: {skills}")
print(f"❌ Missing: {missing}")