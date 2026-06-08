import streamlit as st
import PyPDF2
from openai import OpenAI
import os

st.set_page_config(page_title="Resume Advisor", layout="wide")

# Get API key
GROQ_API_KEY = os.getenv("GROQ_API_KEY", st.secrets.get("GROQ_API_KEY", ""))

client = OpenAI(base_url="https://api.groq.com/openai/v1", api_key=GROQ_API_KEY)

st.title("📄 Smart Resume Career Advisor")

st.markdown("Upload your resume to get AI-powered career advice")

# Market skills
market_skills = ['Python', 'SQL', 'AWS', 'Docker', 'Kubernetes', 'React', 'Node.js', 
                 'Machine Learning', 'Data Analysis', 'Cybersecurity', 'Terraform', 'Git']

uploaded_file = st.file_uploader("Choose PDF file", type="pdf")

if uploaded_file is not None:
    with st.spinner("Analyzing your resume..."):
        # Extract text from PDF
        pdf_reader = PyPDF2.PdfReader(uploaded_file)
        resume_text = ""
        for page in pdf_reader.pages:
            resume_text += page.extract_text()
        
        # Extract skills using AI
        prompt = f"""
        Extract all technical skills from this resume.
        Return only a Python list of skills, nothing else.
        
        Resume: {resume_text[:2000]}
        """
        
        response = client.chat.completions.create(
            model="llama-3.1-8b-instant",
            messages=[{"role": "user", "content": prompt}]
        )
        
        skills = eval(response.choices[0].message.content)
        
        # Compare with market
        your_set = set(s.lower() for s in skills)
        market_set = set(s.lower() for s in market_skills)
        matched = list(your_set & market_set)
        missing = list(market_set - your_set)
        
        # Display results
        st.success("✅ Analysis Complete!")
        
        col1, col2 = st.columns(2)
        with col1:
            st.subheader("📊 Your Skills")
            st.write(skills)
            st.metric("Market Match", f"{len(matched)}/{len(market_skills)}")
        
        with col2:
            st.subheader("🎯 Skills to Learn")
            st.write(missing[:8])
        
        # Generate advice
        advice_prompt = f"""
        User has skills: {skills}
        Missing important skills: {missing[:5]}
        Give 3 short bullet points of career advice.
        """
        
        advice_response = client.chat.completions.create(
            model="llama-3.1-8b-instant",
            messages=[{"role": "user", "content": advice_prompt}]
        )
        
        st.subheader("💡 Career Advice")
        st.info(advice_response.choices[0].message.content)