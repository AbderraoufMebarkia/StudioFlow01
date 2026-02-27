import os
import json
import requests
import streamlit as st
import pandas as pd
from datetime import datetime
from dotenv import load_dotenv

# ==========================================
# 1. INITIALIZATION & CONFIGURATION
# ==========================================
load_dotenv()

st.set_page_config(
    page_title="LaunchPad OS | AI Product Research",
    page_icon="🚀",
    layout="wide",
    initial_sidebar_state="expanded"
)

# OpenRouter Models Configuration
MODEL_GROK = "x-ai/grok-2-1212" # Great for structured generation & strategy
MODEL_DEEPSEEK = "deepseek/deepseek-r1" # Great for deep reasoning & analysis

# Mock User Database
USERS = {
    "founder": {"password": "password", "name": "Startup Founder", "role": "Admin"},
    "researcher": {"password": "password", "name": "Market Researcher", "role": "Analyst"}
}

# ==========================================
# 2. CORE UTILITIES & AI ENGINE (OpenRouter)
# ==========================================
def init_mock_data():
    if "products" not in st.session_state:
        st.session_state.products = pd.DataFrame([
            {"id": "PROD-01", "name": "Ai3DGen", "type": "Digital", "stage": "2. Market Research", "status": "Active"},
            {"id": "PROD-02", "name": "BlenderFlow: Action Engine", "type": "Digital", "stage": "3. Prototyping", "status": "Active"},
            {"id": "PROD-03", "name": "Smart Home Hub", "type": "Physical", "stage": "1. Concept", "status": "Draft"}
        ])
    
    if "canvas" not in st.session_state:
        st.session_state.canvas = {}

def call_openrouter(system_prompt, user_prompt, model=MODEL_DEEPSEEK):
    api_key = os.getenv("OPENROUTER_API_KEY")
    if not api_key:
        try:
            api_key = st.secrets["OPENROUTER_API_KEY"]
        except:
            return "Error: OPENROUTER_API_KEY not found in environment or secrets."
    
    headers = {
        "Authorization": f"Bearer {api_key}",
        "HTTP-Referer": "https://studioflow-app.com", # Update with your real URL
        "X-Title": "LaunchPad OS",
        "Content-Type": "application/json"
    }
    
    data = {
        "model": model,
        "messages": [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_prompt}
        ],
        "temperature": 0.7,
        "max_tokens": 1500
    }
    
    try:
        response = requests.post("https://openrouter.ai/api/v1/chat/completions", headers=headers, json=data)
        response.raise_for_status()
        return response.json()['choices'][0]['message']['content']
    except Exception as e:
        return f"API Error: {str(e)}"

# Specific AI Functions
def ai_generate_canvas(idea_description):
    sys_prompt = "You are a startup expert. Generate a Business Model Canvas based on the user's idea. Output a clean, structured Markdown response with sections: Target Audience, Value Proposition, Channels, Revenue Streams, Cost Structure."
    return call_openrouter(sys_prompt, idea_description, model=MODEL_GROK)

def ai_competitor_analysis(product_niche):
    sys_prompt = "You are a Senior Market Researcher. Analyze the given niche. Identify 3 potential competitors, their strengths, weaknesses, and a potential market gap for a new entrant. Use deep reasoning."
    return call_openrouter(sys_prompt, product_niche, model=MODEL_DEEPSEEK)

def ai_gate_review(project_data):
    sys_prompt = "You are a Stage-Gate review board AI. Analyze the project details. Assess Market Attractiveness, Technical Feasibility, and Risk. Give a GO or NO-GO recommendation with 3 bullet points."
    return call_openrouter(sys_prompt, project_data, model=MODEL_DEEPSEEK)

def ai_marketing_copy(product_name, features):
    sys_prompt = "You are a master copywriter. Create a compelling landing page headline, a subheadline, and 3 bullet points for a launch campaign."
    return call_openrouter(sys_prompt, f"Product: {product_name}\nFeatures: {features}", model=MODEL_GROK)

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
    st.caption("Powered by Grok (via OpenRouter)")
    
    idea = st.text_area("Describe your product idea in a few sentences:", height=150, placeholder="E.g., An AI-powered standalone 3D generation tool for web...")
    
    if st.button("Generate Business Model Canvas", type="primary"):
        if idea:
            with st.spinner("Grok is generating your business model..."):
                canvas_result = ai_generate_canvas(idea)
                st.session_state.canvas[idea[:20]] = canvas_result
                st.markdown(canvas_result)
        else:
            st.warning("Please describe an idea first.")

def render_phase2_market():
    st.header("Phase 2: Market Research & Analysis")
    st.caption("Powered by DeepSeek R1 (via OpenRouter)")
    
    niche = st.text_input("Enter your product niche or industry:")
    
    col1, col2 = st.columns(2)
    with col1:
        if st.button("Run Deep Competitor Analysis", use_container_width=True):
            if niche:
                with st.spinner("DeepSeek is reasoning through market data..."):
                    st.info(ai_competitor_analysis(niche))
            else:
                st.warning("Enter a niche to analyze.")
                
    with col2:
        st.button("Generate Customer Survey Template", use_container_width=True)
        # Placeholder for survey generation logic

def render_phase3_prototype():
    st.header("Phase 3: Design & Prototyping (MVP)")
    st.markdown("Define your **Minimum Viable Product** and build-measure-learn loop.")
    
    product_names = st.session_state.products['name'].tolist()
    selected_proj = st.selectbox("Select Product", product_names)
    
    with st.expander("Define MVP Features"):
        st.text_area("Core feature list for initial launch:")
        st.selectbox("Prototyping Tool Recommendation", ["Figma (Digital UI)", "Three.js/WebGL (Web 3D)", "Blender (Add-on/Mockup)", "CAD/SolidWorks (Physical)"])
        st.button("Save MVP Definition")

def render_phase4_validation():
    st.header("Phase 4: Testing & Stage-Gate Validation")
    
    st.markdown("### 🚦 Official Stage-Gate Review")
    product_data = st.text_area("Paste MVP test results, user feedback summaries, or technical metrics here:")
    
    if st.button("Run AI Gate Assessment (GO / NO-GO)"):
        if product_data:
            with st.spinner("DeepSeek is evaluating gate criteria..."):
                st.success(ai_gate_review(product_data))
        else:
            st.warning("Provide test data for the review board.")

def render_phase5_launch():
    st.header("Phase 5 & 6: Marketing, Launch & Growth")
    
    prod_name = st.text_input("Product Name for Campaign:")
    features = st.text_area("Key Selling Points:")
    
    if st.button("Generate Launch Copy with Grok"):
        if prod_name and features:
            with st.spinner("Crafting high-converting copy..."):
                st.markdown(ai_marketing_copy(prod_name, features))
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
        
        menu = [
            "Dashboard", 
            "1. Concept (Canvas)", 
            "2. Market Research", 
            "3. Prototyping (MVP)", 
            "4. Validation (Stage-Gate)", 
            "5. Launch & Growth"
        ]
        choice = st.radio("Pipeline Stages", menu)
        
        st.divider()
        if st.button("Logout", use_container_width=True):
            logout()

    # Routing logic
    if choice == "Dashboard":
        render_dashboard()
    elif choice == "1. Concept (Canvas)":
        render_phase1_concept()
    elif choice == "2. Market Research":
        render_phase2_market()
    elif choice == "3. Prototyping (MVP)":
        render_phase3_prototype()
    elif choice == "4. Validation (Stage-Gate)":
        render_phase4_validation()
    elif choice == "5. Launch & Growth":
        render_phase5_launch()

if __name__ == "__main__":
    main()
