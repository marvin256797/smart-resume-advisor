import streamlit as st
import os
from supabase import create_client
import PyPDF2
from openai import OpenAI

# Page config
st.set_page_config(page_title="Resume Advisor", layout="wide")

# Get secrets
try:
    SUPABASE_URL = st.secrets["SUPABASE_URL"]
    SUPABASE_KEY = st.secrets["SUPABASE_KEY"]
    GROQ_API_KEY = st.secrets["GROQ_API_KEY"]
except:
    SUPABASE_URL = os.getenv("SUPABASE_URL")
    SUPABASE_KEY = os.getenv("SUPABASE_KEY")
    GROQ_API_KEY = os.getenv("GROQ_API_KEY")

# Initialize clients
supabase = create_client(SUPABASE_URL, SUPABASE_KEY)
client = OpenAI(base_url="https://api.groq.com/openai/v1", api_key=GROQ_API_KEY)

st.title("📄 Smart Resume Career Advisor")

# Simple login
if 'user' not in st.session_state:
    st.session_state.user = None

if st.session_state.user is None:
    st.subheader("Login")
    email = st.text_input("Email")
    password = st.text_input("Password", type="password")
    
    if st.button("Sign In"):
        try:
            result = supabase.auth.sign_in_with_password({"email": email, "password": password})
            st.session_state.user = result.user
            st.rerun()
        except Exception as e:
            st.error(f"Login failed: {e}")
    
    if st.button("Create Account"):
        try:
            result = supabase.auth.sign_up({"email": email, "password": password})
            supabase.table("profiles").insert({"id": result.user.id, "email": email}).execute()
            st.success("Account created! Please sign in.")
        except Exception as e:
            st.error(f"Signup failed: {e}")

else:
    st.success(f"Welcome, {st.session_state.user.email}")
    
    if st.button("Logout"):
        st.session_state.user = None
        st.rerun()
    
    uploaded_file = st.file_uploader("Upload Resume (PDF)", type="pdf")
    
    if uploaded_file:
        with st.spinner("Analyzing..."):
            # Extract text
            pdf_reader = PyPDF2.PdfReader(uploaded_file)
            text = "".join([page.extract_text() for page in pdf_reader.pages])
            
            # Extract skills using AI
            response = client.chat.completions.create(
                model="llama-3.1-8b-instant",
                messages=[{"role": "user", "content": f"Extract skills as Python list from: {text[:1500]}"}]
            )
            skills = eval(response.choices[0].message.content)
            
            st.subheader("✅ Your Skills")
            st.write(skills)
            
            # Save to database
            supabase.table("resume_analyses").insert({
                "user_id": st.session_state.user.id,
                "extracted_skills": skills,
                "file_name": uploaded_file.name
            }).execute()
            
            st.success("Saved to database!")