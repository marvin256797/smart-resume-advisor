import streamlit as st
import os
from dotenv import load_dotenv
from supabase import create_client
import pandas as pd
from openai import OpenAI
import PyPDF2
import plotly.express as px

pass

# Setup
supabase = create_client(
    os.getenv("SUPABASE_URL"),
    os.getenv("SUPABASE_KEY")
)

client = OpenAI(
    base_url="https://api.groq.com/openai/v1",
    api_key=os.getenv("GROQ_API_KEY")
)

# Page config
st.set_page_config(page_title="Resume Advisor", page_icon="📄", layout="wide")

# Custom CSS for better UI
st.markdown("""
<style>
    .main-header {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        padding: 2rem;
        border-radius: 10px;
        color: white;
        text-align: center;
        margin-bottom: 2rem;
    }
    .skill-badge {
        background-color: #4CAF50;
        color: white;
        padding: 5px 10px;
        border-radius: 15px;
        display: inline-block;
        margin: 3px;
        font-size: 12px;
    }
    .missing-badge {
        background-color: #f44336;
        color: white;
        padding: 5px 10px;
        border-radius: 15px;
        display: inline-block;
        margin: 3px;
        font-size: 12px;
    }
    .metric-card {
        background-color: #f0f2f6;
        padding: 1rem;
        border-radius: 10px;
        text-align: center;
    }
</style>
""", unsafe_allow_html=True)

# Header
st.markdown("""
<div class="main-header">
    <h1>🚀 Smart Resume Career Advisor</h1>
    <p>AI-powered resume analysis to boost your career</p>
</div>
""", unsafe_allow_html=True)

# Market skills
market_skills = ['Python', 'SQL', 'AWS', 'Docker', 'Kubernetes', 'React', 'Node.js', 
                 'Machine Learning', 'Data Analysis', 'Cybersecurity', 'Terraform', 'Git', 
                 'FastAPI', 'PostgreSQL', 'MongoDB', 'CI/CD', 'Redis', 'TensorFlow']

# Sidebar
with st.sidebar:
    st.image("https://img.icons8.com/color/96/000000/resume.png", width=80)
    st.markdown("## 📋 Navigation")
    option = st.radio("", ["📤 Upload Resume", "📊 View History", "📈 Market Insights", "🎯 Skill Gap"])
    
    st.markdown("---")
    st.markdown("### 🎓 Pro Tip")
    st.info("Upload your resume as PDF to get personalized career recommendations based on 2026 market demands.")
    
    st.markdown("---")
    st.markdown("Made with ❤️ using Groq AI & Supabase")

def extract_skills_from_text(resume_text):
    prompt = f"""
    Extract all technical and professional skills from this resume.
    Return only a Python list of skills, nothing else.
    Resume text: {resume_text[:2000]}
    """
    response = client.chat.completions.create(
        model="llama-3.1-8b-instant",
        messages=[{"role": "user", "content": prompt}]
    )
    return eval(response.choices[0].message.content)

def get_recommendation(skills, missing):
    prompt = f"""
    User has skills: {skills}
    Missing skills: {missing}
    Give 4 bullet points of specific career advice. Be actionable and practical.
    """
    response = client.chat.completions.create(
        model="llama-3.1-8b-instant",
        messages=[{"role": "user", "content": prompt}]
    )
    return response.choices[0].message.content

# Page: Upload Resume
if option == "📤 Upload Resume":
    col1, col2 = st.columns([1, 1])
    
    with col1:
        st.markdown("### 📄 Upload Your Resume")
        uploaded_file = st.file_uploader("Choose PDF file", type="pdf", label_visibility="collapsed")
        
        if uploaded_file is not None:
            with st.spinner("🔍 Analyzing your resume..."):
                # Extract text
                pdf_reader = PyPDF2.PdfReader(uploaded_file)
                resume_text = ""
                for page in pdf_reader.pages:
                    resume_text += page.extract_text()
                
                # Extract skills
                skills = extract_skills_from_text(resume_text)
                
                # Find gaps
                your_set = set(s.lower() for s in skills)
                market_set = set(s.lower() for s in market_skills)
                missing = list(market_set - your_set)
                matched = list(your_set & market_set)
                
                # Get recommendation
                recommendation = get_recommendation(skills, missing)
                
                # Save to database
                data = {
                    "resume_text": resume_text[:500],
                    "extracted_skills": skills,
                    "missing_skills": missing,
                    "recommendation": recommendation,
                    "file_name": uploaded_file.name
                }
                supabase.table("resume_analyses").insert(data).execute()
                
                # Display results
                st.session_state['last_analysis'] = {
                    'skills': skills,
                    'missing': missing,
                    'matched': matched,
                    'recommendation': recommendation
                }
                st.success("✅ Analysis Complete!")
    
    if 'last_analysis' in st.session_state:
        data = st.session_state['last_analysis']
        
        with col2:
            # Metrics
            col_a, col_b, col_c = st.columns(3)
            with col_a:
                st.markdown(f"""
                <div class="metric-card">
                    <h3>📊 {len(data['skills'])}</h3>
                    <p>Your Skills</p>
                </div>
                """, unsafe_allow_html=True)
            with col_b:
                st.markdown(f"""
                <div class="metric-card">
                    <h3>📈 {len(data['matched'])}</h3>
                    <p>Market Match</p>
                </div>
                """, unsafe_allow_html=True)
            with col_c:
                st.markdown(f"""
                <div class="metric-card">
                    <h3>🎯 {(len(data['matched'])/len(market_skills)*100):.0f}%</h3>
                    <p>Compatibility</p>
                </div>
                """, unsafe_allow_html=True)
        
        # Skills display
        st.markdown("---")
        col1, col2 = st.columns(2)
        
        with col1:
            st.markdown("### ✅ Your Skills")
            st.markdown(f"<div>{''.join([f'<span class=\"skill-badge\">{s}</span>' for s in data['skills']])}</div>", unsafe_allow_html=True)
        
        with col2:
            st.markdown("### ❌ Missing Skills")
            if data['missing']:
                st.markdown(f"<div>{''.join([f'<span class=\"missing-badge\">{m}</span>' for m in data['missing'][:10]])}</div>", unsafe_allow_html=True)
            else:
                st.success("🎉 You have all market skills!")
        
        # Recommendation
        st.markdown("---")
        st.markdown("### 💡 AI Career Recommendation")
        st.info(recommendation)
        
        # Progress chart
        st.markdown("---")
        st.markdown("### 📊 Skill Gap Visualization")
        progress_df = pd.DataFrame({
            'Category': ['Matched Skills', 'Missing Skills'],
            'Count': [len(data['matched']), len(data['missing'])]
        })
        fig = px.pie(progress_df, values='Count', names='Category', 
                     color_discrete_sequence=['#4CAF50', '#f44336'])
        st.plotly_chart(fig, use_container_width=True)

# Page: View History
elif option == "📊 View History":
    st.markdown("### 📜 Analysis History")
    result = supabase.table("resume_analyses").select("*").order("created_at", desc=True).execute()
    df = pd.DataFrame(result.data)
    
    if not df.empty:
        for _, row in df.iterrows():
            with st.expander(f"📄 {row['file_name']} - {row['created_at'][:10]}"):
                col1, col2 = st.columns(2)
                with col1:
                    st.markdown("**Your Skills:**")
                    st.write(row['extracted_skills'])
                with col2:
                    st.markdown("**Missing:**")
                    st.write(row['missing_skills'][:5])
                st.markdown("**Recommendation:**")
                st.info(row['recommendation'][:300] + "...")
    else:
        st.info("No analyses yet. Upload a resume first.")

# Page: Market Insights
elif option == "📈 Market Insights":
    st.markdown("### 🔥 Top In-Demand Skills (2026)")
    
    # Create skill demand data
    skill_data = pd.DataFrame({
        'Skill': market_skills,
        'Importance': list(range(len(market_skills), 0, -1))
    })
    
    fig = px.bar(skill_data, x='Importance', y='Skill', orientation='h',
                 title='Most Valuable Skills for 2026',
                 color='Importance', color_continuous_scale='Viridis')
    st.plotly_chart(fig, use_container_width=True)
    
    st.markdown("### 📈 Trending Technologies")
    col1, col2, col3 = st.columns(3)
    with col1:
        st.markdown("""
        **🚀 High Growth**
        - AI/ML Engineering
        - Cloud Security
        - Data Engineering
        """)
    with col2:
        st.markdown("""
        **💪 Stable Demand**
        - Python
        - SQL
        - JavaScript
        """)
    with col3:
        st.markdown("""
        **🌟 Emerging**
        - Prompt Engineering
        - Vector Databases
        - MLOps
        """)

# Page: Skill Gap
elif option == "🎯 Skill Gap":
    st.markdown("### 🎯 Identify Your Skill Gap")
    
    your_input = st.text_area("Paste your skills (comma-separated)", 
                               placeholder="Example: Python, JavaScript, SQL")
    
    if st.button("Analyze Gap"):
        your_skills = [s.strip().lower() for s in your_input.split(",")]
        market_set = set(s.lower() for s in market_skills)
        your_set = set(your_skills)
        
        matched = list(market_set & your_set)
        missing = list(market_set - your_set)
        
        col1, col2 = st.columns(2)
        with col1:
            st.markdown(f"✅ **Matched:** {len(matched)} skills")
            st.write(matched[:10])
        with col2:
            st.markdown(f"❌ **Missing:** {len(missing)} skills")
            st.write(missing[:10])
        
        if missing:
            st.markdown("### 📝 Quick Recommendation")
            rec = get_recommendation(your_skills, missing[:5])
            st.info(rec)
