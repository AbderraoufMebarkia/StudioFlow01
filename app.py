import os
import streamlit as st
import pandas as pd
from datetime import datetime
from groq import Groq
from openai import OpenAI  # نستخدمها للاتصال بـ DeepSeek

# ==========================================
# 1. INITIALIZATION & CONFIGURATION
# ==========================================
st.set_page_config(
    page_title="LaunchPad OS | AI Product Research",
    page_icon="🚀",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Models Configuration
GROQ_MODEL = "llama-3.3-70b-versatile" 
DEEPSEEK_MODEL = "deepseek-reasoner" # نموذج التفكير العميق الأحدث R1

# Mock User Database
USERS = {
    "founder": {"password": "password", "name": "Startup Founder", "role": "Admin"},
    "researcher": {"password": "password", "name": "Market Researcher", "role": "Analyst"}
}

# ==========================================
# 2. CORE UTILITIES & DUAL AI ENGINE
# ==========================================
def init_mock_data():
    if "products" not in st.session_state:
        st.session_state.products = pd.DataFrame([
            {"id": "PROD-01", "name": "Ai3DGen", "type": "Digital", "stage": "2. Market Research", "status": "Active"},
            {"id": "PROD-02", "name": "BlenderFlow", "type": "Digital", "stage": "3. Prototyping", "status": "Active"},
            {"id": "PROD-03", "name": "Smart Home Hub", "type": "Physical", "stage": "1. Concept", "status": "Draft"}
        ])
    
    if "canvas" not in st.session_state:
        st.session_state.canvas = {}

# محرك الذكاء الاصطناعي المزدوج الذي يقرأ اختيارك من القائمة الجانبية
def call_ai(system_prompt, user_prompt):
    provider = st.session_state.get("ai_provider", "Groq (Llama 3.3)")
    
    if "Groq" in provider:
        api_key = os.getenv("GROQ_API_KEY") or st.secrets.get("GROQ_API_KEY")
        if not api_key: return "Error: GROQ_API_KEY is missing."
        
        client = Groq(api_key=api_key)
        try:
            completion = client.chat.completions.create(
                model=GROQ_MODEL,
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_prompt}
                ],
                temperature=0.6,
                max_tokens=1500
            )
            return completion.choices[0].message.content
        except Exception as e:
            return f"Groq API Error: {str(e)}"
            
    elif "DeepSeek" in provider:
        api_key = os.getenv("DEEPSEEK_API_KEY") or st.secrets.get("DEEPSEEK_API_KEY")
        if not api_key: return "Error: DEEPSEEK_API_KEY is missing."
        
        # DeepSeek يستخدم بروتوكول متوافق مع OpenAI
        client = OpenAI(api_key=api_key, base_url="https://api.deepseek.com")
        try:
            completion = client.chat.completions.create(
                model=DEEPSEEK_MODEL,
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_prompt}
                ],
                max_tokens=2000
            )
            return completion.choices[0].message.content
        except Exception as e:
            return f"DeepSeek API Error: {str(e)}"

# ==========================================
# 3. AUTHENTICATION MODULE
# ==========================================
def check_auth():
    return st.session_state.get("authenticated", False)

def login_ui():
    st.markdown("<h1 style='text-align: center;'>🚀 LaunchPad OS</h1>", unsafe_allow_html=True)
    st.markdown("<p style='text-align: center;'>AI-Powered Product Research & Launch Platform</p>", unsafe_allow_html=True)
    
    col1, col2, col3 = st.columns([1, 1, 1])
    with col2:
        with st.form("login_form"):
            username = st.text_input("Username (founder)")
            password = st.text_input("Password (password)", type="password")
            submit = st.form_submit_button("Sign In", use_container_width=True)
            
            if submit:
                if username in USERS and USERS[username]["password"] == password:
                    st.session_state["authenticated"] = True
                    st.session_state["user"] = USERS[username]
                    st.rerun()
                else:
                    st.error("Invalid credentials.")

def logout():
    st.session_state["authenticated"] = False
    st.session_state["user"] = None
    st.rerun()

# ==========================================
# 4. STAGE-GATE MODULES (UI RENDERERS)
# ==========================================
def render_dashboard():
    st.header("🏢 Portfolio Dashboard")
    st.markdown("Overview of all active product concepts and their current Stage-Gate status.")
    
    df = st.session_state.products
    
    col1, col2, col3 = st.columns(3)
    col1.metric("Active Concepts", len(df[df['status'] == 'Active']))
    col2.metric("Products in Concept Stage", len(df[df['stage'] == '1. Concept']))
    col3.metric("Ready for Launch", len(df[df['stage'] == '5. Marketing & Launch']))
    
    st.divider()
    st.subheader("Product Pipeline")
    st.dataframe(df, use_container_width=True, hide_index=True)

def render_phase1_concept():
    st.header("Phase 1: Concept Definition")
    st.caption(f"Currently using: {st.session_state.get('ai_provider')}")
    
    idea = st.text_area("Describe your product idea in a few sentences:", height=150)
    
    if st.button("Generate Business Model Canvas", type="primary"):
        if idea:
            with st.spinner("Analyzing and building canvas..."):
                sys_prompt = "You are a startup expert. Generate a Business Model Canvas. Use clear Markdown."
                canvas_result = call_ai(sys_prompt, idea)
                st.session_state.canvas[idea[:20]] = canvas_result
                st.markdown(canvas_result)
        else:
            st.warning("Please describe an idea first.")

def render_phase2_market():
    st.header("Phase 2: Market Research & Analysis")
    st.caption(f"Currently using: {st.session_state.get('ai_provider')}")
    
    niche = st.text_input("Enter your product niche or industry:")
    
    if st.button("Run Deep Competitor Analysis", type="primary"):
        if niche:
            with st.spinner("Processing market data..."):
                sys_prompt = "You are a Senior Market Researcher. Analyze the given niche, identify 3 competitors, and find market gaps."
                st.info(call_ai(sys_prompt, niche))
        else:
            st.warning("Enter a niche to analyze.")

def render_phase3_prototype():
    st.header("Phase 3: Design & Prototyping (MVP)")
    
    product_names = st.session_state.products['name'].tolist()
    st.selectbox("Select Product", product_names)
    
    with st.expander("Define MVP Features", expanded=True):
        st.text_area("Core feature list for initial launch:")
        st.selectbox("Prototyping Tool Recommendation", ["Figma (Digital UI)", "Three.js/WebGL (Web 3D)", "Blender (Add-on/Mockup)", "CAD/SolidWorks (Physical)"])
        if st.button("Save MVP Definition"):
            st.success("MVP definition saved successfully.")

def render_phase4_validation():
    st.header("Phase 4: Testing & Stage-Gate Validation")
    st.caption(f"Currently using: {st.session_state.get('ai_provider')}")
    
    product_data = st.text_area("Paste MVP test results, user feedback summaries, or technical metrics here:", height=150)
    
    if st.button("Run AI Gate Assessment (GO / NO-GO)"):
        if product_data:
            with st.spinner("Evaluating gate criteria..."):
                sys_prompt = "You are a Stage-Gate review board AI. Assess Market Attractiveness, Technical Feasibility, and Risk. Give a GO or NO-GO recommendation."
                st.success(call_ai(sys_prompt, product_data))
        else:
            st.warning("Provide test data for the review board.")

def render_phase5_launch():
    st.header("Phase 5: Marketing & Launch")
    st.caption(f"Currently using: {st.session_state.get('ai_provider')}")
    
    prod_name = st.text_input("Product Name for Campaign:")
    features = st.text_area("Key Selling Points:")
    
    if st.button("Generate Launch Copy"):
        if prod_name and features:
            with st.spinner("Crafting high-converting copy..."):
                sys_prompt = "You are a master copywriter. Create a compelling landing page headline, subheadline, and 3 bullet points."
                st.markdown(call_ai(sys_prompt, f"Product: {prod_name}\nFeatures: {features}"))
        else:
            st.warning("Fill in product details.")

# ==========================================
# 5. MAIN APPLICATION ROUTER
# ==========================================
def main():
    init_mock_data()
    
    if not check_auth():
        login_ui()
        return

    with st.sidebar:
        st.title("🚀 LaunchPad OS")
        st.caption(f"User: **{st.session_state.user['name']}**")
        st.divider()
        
        # 🧠 زر تبديل محرك الذكاء الاصطناعي
        st.subheader("🧠 AI Engine")
        st.radio(
            "Select Processing Engine:",
            ["Groq (Llama 3.3)", "DeepSeek (Reasoner)"],
            key="ai_provider",
            help="Choose Groq for speed, or DeepSeek for deep analysis."
        )
        st.divider()
        
        menu = [
            "Dashboard", 
            "1. Concept (Canvas)", 
            "2. Market Research", 
            "3. Prototyping (MVP)", 
            "4. Validation (Stage-Gate)", 
            "5. Marketing & Launch"
        ]
        choice = st.radio("Pipeline Stages", menu)
        
        st.divider()
        if st.button("Logout", use_container_width=True):
            logout()

    if choice == "Dashboard": render_dashboard()
    elif choice == "1. Concept (Canvas)": render_phase1_concept()
    elif choice == "2. Market Research": render_phase2_market()
    elif choice == "3. Prototyping (MVP)": render_phase3_prototype()
    elif choice == "4. Validation (Stage-Gate)": render_phase4_validation()
    elif choice == "5. Marketing & Launch": render_phase5_launch()

if __name__ == "__main__":
    main()
