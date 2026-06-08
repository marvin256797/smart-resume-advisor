import streamlit as st
import os
from supabase import create_client
import pandas as pd
import PyPDF2
from openai import OpenAI
import plotly.express as px
from datetime import datetime

# Page config
st.set_page_config(page_title="Resume Advisor", page_icon="📄", layout="wide")

# Initialize Supabase
supabase = create_client(
    st.secrets["SUPABASE_URL"],
    st.secrets["SUPABASE_KEY"]
)

# Initialize Groq
client = OpenAI(
    base_url="https://api.groq.com/openai/v1",
    api_key=st.secrets["GROQ_API_KEY"]
)

# Market skills
market_skills = ['Python', 'SQL', 'AWS', 'Docker', 'Kubernetes', 'React', 'Node.js', 
                 'Machine Learning', 'Data Analysis', 'Cybersecurity', 'Terraform', 'Git', 
                 'FastAPI', 'PostgreSQL', 'MongoDB', 'CI/CD', 'Redis', 'TensorFlow']

# Custom CSS
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

# Session state for login
if 'logged_in' not in st.session_state:
    st.session_state.logged_in = False
if 'user_email' not in st.session_state:
    st.session_state.user_email = None
if 'user_id' not in st.session_state:
    st.session_state.user_id = None

def sign_up(email, password):
    try:
        response = supabase.auth.sign_up({
            "email": email,
            "password": password
        })
        # Create profile
        supabase.table("profiles").insert({
            "id": response.user.id,
            "email": email
        }).execute()
        return True, response
    except Exception as e:
        return False, str(e)

def sign_in(email, password):
    try:
        response = supabase.auth.sign_in({
            "email": email,
            "password": password
        })
        return True, response
    except Exception as e:
        return False, str(e)

def sign_out():
    supabase.auth.sign_out()
    st.session_state.logged_in = False
    st.session_state.user_email = None
    st.session_state.user_id = None

def extract_skills(resume_text):
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
    Give 4 bullet points of specific career advice. Be actionable.
    """
    response = client.chat.completions.create(
        model="llama-3.1-8b-instant",
        messages=[{"role": "user", "content": prompt}]
    )
    return response.choices[0].message.content

# Login/Logout UI
if not st.session_state.logged_in:
    st.markdown("""
    <div class="main-header">
        <h1>🚀 Smart Resume Career Advisor</h1>
        <p>Sign in to get personalized AI-powered career advice</p>
    </div>
    """, unsafe_allow_html=True)
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("🔐 Sign In")
        email = st.text_input("Email", key="login_email")
        password = st.text_input("Password", type="password", key="login_password")
        if st.button("Sign In", type="primary"):
            success, result = sign_in(email, password)
            if success:
                st.session_state.logged_in = True
                st.session_state.user_email = email
                st.session_state.user_id = result.user.id
                st.rerun()
            else:
                st.error(f"Login failed: {result}")
    
    with col2:
        st.subheader("📝 Sign Up")
        new_email = st.text_input("Email", key="signup_email")
        new_password = st.text_input("Password", type="password", key="signup_password")
        confirm_password = st.text_input("Confirm Password", type="password")
        if st.button("Create Account"):
            if new_password != confirm_password:
                st.error("Passwords do not match")
            else:
                success, result = sign_up(new_email, new_password)
                if success:
                    st.success("Account created! Please sign in.")
                else:
                    st.error(f"Signup failed: {result}")

else:
    # Header with logout
    st.markdown(f"""
    <div class="main-header">
        <h1>🚀 Smart Resume Career Advisor</h1>
        <p>Welcome, {st.session_state.user_email}!</p>
    </div>
    """, unsafe_allow_html=True)
    
    # Sidebar
    with st.sidebar:
        st.image("https://img.icons8.com/color/96/000000/resume.png", width=80)
        st.markdown(f"**User:** {st.session_state.user_email}")
        st.markdown("---")
        option = st.radio("📋 Navigation", ["📤 Upload Resume", "📊 My History", "📈 Market Insights", "🎯 Skill Gap"])
        st.markdown("---")
        if st.button("🚪 Sign Out"):
            sign_out()
            st.rerun()
        st.markdown("---")
        st.markdown("Made with ❤️ using Groq AI & Supabase")
    
    # Function to get user's history
    def get_user_history():
        result = supabase.table("resume_analyses") \
            .select("*") \
            .eq("user_id", st.session_state.user_id) \
            .order("created_at", desc=True) \
            .execute()
        return result.data
    
    # Page: Upload Resume
    if option == "📤 Upload Resume":
        uploaded_file = st.file_uploader("Upload PDF Resume", type="pdf")
        
        if uploaded_file is not None:
            with st.spinner("🔍 Analyzing..."):
                # Extract text
                pdf_reader = PyPDF2.PdfReader(uploaded_file)
                resume_text = ""
                for page in pdf_reader.pages:
                    resume_text += page.extract_text()
                
                # Extract skills
                skills = extract_skills(resume_text)
                
                # Find gaps
                your_set = set(s.lower() for s in skills)
                market_set = set(s.lower() for s in market_skills)
                missing = list(market_set - your_set)
                matched = list(your_set & market_set)
                
                # Get recommendation
                recommendation = get_recommendation(skills, missing)
                
                # Save to database with user_id
                data = {
                    "user_id": st.session_state.user_id,
                    "resume_text": resume_text[:500],
                    "extracted_skills": skills,
                    "missing_skills": missing,
                    "recommendation": recommendation,
                    "file_name": uploaded_file.name
                }
                supabase.table("resume_analyses").insert(data).execute()
                
                # Display results
                col1, col2 = st.columns(2)
                with col1:
                    st.subheader("✅ Your Skills")
                    st.write(skills)
                with col2:
                    st.subheader("❌ Missing Skills")
                    st.write(missing[:10])
                
                st.subheader("💡 Recommendation")
                st.info(recommendation)
                
                # Progress
                match_percent = int(len(matched)/len(market_skills)*100)
                st.progress(match_percent/100)
                st.caption(f"Market match: {match_percent}%")
    
    # Page: My History
    elif option == "📊 My History":
        st.subheader("Your Analysis History")
        history = get_user_history()
        
        if history:
            df = pd.DataFrame(history)
            for _, row in df.iterrows():
                with st.expander(f"📄 {row['file_name']} - {row['created_at'][:10]}"):
                    st.write("**Skills:**", row['extracted_skills'])
                    st.write("**Missing:**", row['missing_skills'][:5])
                    st.info(row['recommendation'][:200] + "...")
        else:
            st.info("No analyses yet. Upload a resume first.")
    
    # Page: Market Insights
    elif option == "📈 Market Insights":
        st.subheader("Top In-Demand Skills 2026")
        skill_df = pd.DataFrame({'Skill': market_skills[:15], 'Demand': range(15, 0, -1)})
        fig = px.bar(skill_df, x='Demand', y='Skill', orientation='h', title="Most Valuable Skills")
        st.plotly_chart(fig, use_container_width=True)
    
    # Page: Skill Gap
    elif option == "🎯 Skill Gap":
        st.subheader("Quick Skill Gap Analysis")
        skills_input = st.text_area("Enter your skills (comma-separated)")
        if st.button("Analyze"):
            user_skills = [s.strip().lower() for s in skills_input.split(",")]
            market_set = set(s.lower() for s in market_skills)
            matched = list(market_set & set(user_skills))
            missing = list(market_set - set(user_skills))
            
            st.write(f"✅ Matched: {len(matched)} skills")
            st.write(f"❌ Missing: {len(missing)} skills")
            if missing:
                st.write("Top missing:", missing[:10])