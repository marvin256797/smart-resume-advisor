import os
from openai import OpenAI

os.environ["GROQ_API_KEY"] = "YOUR_GROQ_KEY_HERE"

client = OpenAI(
    base_url="https://api.groq.com/openai/v1",
    api_key=os.environ["GROQ_API_KEY"]
)

# Your extracted skills from resume
your_skills = ['Python', 'JavaScript', 'Django', 'React', 'PostgreSQL', 'AWS', 'Docker', 'Git']

# Top in-demand skills for 2026
market_skills = [
    'Python', 'SQL', 'AWS', 'Docker', 'Kubernetes', 'React', 'Node.js',
    'Machine Learning', 'Data Analysis', 'Cybersecurity', 'Terraform', 'Git'
]

def analyze_gap(your_skills, market_skills):
    your_set = set(skill.lower() for skill in your_skills)
    market_set = set(skill.lower() for skill in market_skills)
    
    missing = list(market_set - your_set)
    matched = list(your_set & market_set)
    
    prompt = f"""
    User has these skills: {your_skills}
    Market demands these skills: {market_skills}
    Missing skills: {missing}
    
    Provide a short career recommendation (3 sentences max).
    """
    
    response = client.chat.completions.create(
        model="llama-3.1-8b-instant",
        messages=[{"role": "user", "content": prompt}]
    )
    
    return response.choices[0].message.content, missing, matched

recommendation, missing, matched = analyze_gap(your_skills, market_skills)

print(f"✅ Your matched skills: {len(matched)} - {matched}")
print(f"❌ Missing skills: {missing}")
print(f"\n📝 Recommendation:\n{recommendation}")
