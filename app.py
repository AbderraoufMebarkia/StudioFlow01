import os
import streamlit as st
import pandas as pd
from datetime import datetime, timedelta
from dotenv import load_dotenv
from groq import Groq

# ==========================================
# 1. INITIALIZATION & CONFIGURATION
# ==========================================
load_dotenv()

st.set_page_config(
    page_title="StudioFlow | AI Production OS",
    page_icon="🎬",
    layout="wide",
    initial_sidebar_state="expanded"
)

# AI Model Configuration
MODEL_NAME = "llama-3.3-70b-versatile"

# Mock User Database
USERS = {
    "admin": {"password": "password", "name": "System Admin", "role": "Admin"},
    "director": {"password": "password", "name": "Lead Director", "role": "Director"},
    "artist": {"password": "password", "name": "Senior CGI Artist", "role": "Artist"}
}

# ==========================================
# 2. CORE UTILITIES & AI ENGINE
# ==========================================
def init_mock_data():
    if "projects" not in st.session_state:
        st.session_state.projects = pd.DataFrame([
            {"id": "PRJ-001", "name": "QLED PRO V8 Launch", "stage": "Post-production", "budget": 150000, "spent": 142000, "deadline": (datetime.now() + timedelta(days=5)).strftime("%Y-%m-%d"), "status": "Delayed"},
            {"id": "PRJ-002", "name": "i5 Pro CGI Commercial", "stage": "Production", "budget": 85000, "spent": 40000, "deadline": (datetime.now() + timedelta(days=30)).strftime("%Y-%m-%d"), "status": "On Track"},
            {"id": "PRJ-003", "name": "Peptiva Rx Visuals", "stage": "Delivery", "budget": 1600, "spent": 1600, "deadline": (datetime.now() - timedelta(days=2)).strftime("%Y-%m-%d"), "status": "Completed"}
        ])
    
    if "assets" not in st.session_state:
        st.session_state.assets = [
            {"name": "i5_pro_exploded_view_v3.blend", "type": "3D Model", "tags": ["CGI", "Technical", "Approved"], "version": 3},
            {"name": "qled_screen_shader_v1.nodes", "type": "Shader", "tags": ["Cycles", "WIP"], "version": 1}
        ]
        
    if "comments" not in st.session_state:
        st.session_state.comments = [
            {"project": "QLED PRO V8 Launch", "author": "Lead Director", "text": "Need to fix the geometry nodes on the particle sim.", "time": "10:30 AM"}
        ]

def get_groq_client():
    api_key = os.getenv("GROQ_API_KEY")
    if not api_key:
        try:
            api_key = st.secrets["GROQ_API_KEY"]
        except:
            return None
    return Groq(api_key=api_key)

def call_groq(system_prompt, user_prompt):
    client = get_groq_client()
    if not client:
        return "Error: GROQ_API_KEY not found in environment variables or Streamlit secrets."
    
    try:
        completion = client.chat.completions.create(
            model=MODEL_NAME,
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt}
            ],
            temperature=0.7,
            max_tokens=1024
        )
        return completion.choices[0].message.content
    except Exception as e:
        return f"API Error: {str(e)}"

def ai_generate_storyboard(script):
    sys_prompt = "You are a master cinematic storyboard artist. Break down the provided script into distinct visual shots. For each shot provide: Shot Number, Camera Angle, Lighting, and Action Description."
    return call_groq(sys_prompt, f"Script:\n{script}")

def ai_analyze_scene(scene_desc):
    sys_prompt = "You are a Senior VFX Supervisor. Analyze the scene description for potential technical challenges, render time risks, and suggest optimizations (e.g., using specific shaders, baking lighting, or geometry nodes approaches)."
    return call_groq(sys_prompt, f"Scene Description:\n{scene_desc}")

def ai_auto_tag_assets(asset_name, asset_desc):
    sys_prompt = "You are an AI pipeline assistant. Based on the file name and description, output a comma-separated list of 5 highly relevant metadata tags for a digital asset management system. Output ONLY the tags."
    return call_groq(sys_prompt, f"File: {asset_name}\nDescription: {asset_desc}")

def ai_optimize_production(project_data):
    sys_prompt = "You are an Executive Producer AI. Analyze the project data (Budget, Spent, Deadline, Stage) and provide a concise risk assessment and 3 actionable steps to optimize delivery."
    return call_groq(sys_prompt, f"Project Data:\n{project_data}")

# ==========================================
# 3. AUTHENTICATION MODULE
# ==========================================
def check_auth():
    return st.session_state.get("authenticated", False)

def login_ui():
    st.markdown("<h1 style='text-align: center;'>StudioFlow Login</h1>", unsafe_allow_html=True)
    st.markdown("<p style='text-align: center;'>AI Production OS</p>", unsafe_allow_html=True)
    
    col1, col2, col3 = st.columns([1, 1, 1])
    with col2:
        with st.form("login_form"):
            username = st.text_input("Username (admin, director, artist)")
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
# 4. FEATURE MODULES (UI RENDERERS)
# ==========================================
def render_dashboard():
    st.header("Executive Dashboard")
    st.markdown("Overview of studio operations and high-level metrics.")
    
    df = st.session_state.projects
    
    col1, col2, col3, col4 = st.columns(4)
    col1.metric("Active Projects", len(df[df['status'] != 'Completed']))
    col2.metric("Total Budget Allocated", f"${df['budget'].sum():,}")
    col3.metric("Total Spent", f"${df['spent'].sum():,}")
    col4.metric("Delayed Projects", len(df[df['status'] == 'Delayed']), delta="-1", delta_color="inverse")
    
    st.divider()
    st.subheader("Active Pipeline")
    st.dataframe(df, use_container_width=True, hide_index=True)

def render_projects():
    st.header("Project Management Engine")
    
    with st.expander("➕ Create New Project"):
        with st.form("new_project_form"):
            col1, col2 = st.columns(2)
            name = col1.text_input("Project Name")
            stage = col2.selectbox("Production Stage", ["Pre-production", "Production", "Post-production", "Delivery"])
            budget = col1.number_input("Budget ($)", min_value=0, step=1000)
            deadline = col2.date_input("Deadline")
            
            if st.form_submit_button("Initialize Project"):
                new_row = {"id": f"PRJ-{len(st.session_state.projects)+1:03d}", "name": name, "stage": stage, "budget": budget, "spent": 0, "deadline": deadline.strftime("%Y-%m-%d"), "status": "On Track"}
                st.session_state.projects = pd.concat([st.session_state.projects, pd.DataFrame([new_row])], ignore_index=True)
                st.success(f"Project '{name}' initialized successfully.")
                st.rerun()

    st.subheader("Project Directory")
    for index, row in st.session_state.projects.iterrows():
        with st.container(border=True):
            cols = st.columns([3, 2, 2, 2])
            cols[0].markdown(f"**{row['name']}** ({row['id']})")
            cols[1].caption(f"Stage: {row['stage']}")
            cols[2].caption(f"Status: {row['status']}")
            budget_pct = int((row['spent'] / row['budget']) * 100) if row['budget'] > 0 else 0
            cols[3].progress(budget_pct / 100, text=f"{budget_pct}% Budget")

def render_assets():
    st.header("Asset Management")
    
    col1, col2 = st.columns([1, 2])
    
    with col1:
        st.subheader("Upload Asset")
        uploaded_file = st.file_uploader("Drop production files here (.blend, .exr, .mp4)")
        asset_desc = st.text_area("Optional Description")
        
        if uploaded_file and st.button("Process & Auto-Tag", type="primary"):
            with st.spinner("AI analyzing asset context..."):
                tags = ai_auto_tag_assets(uploaded_file.name, asset_desc)
                new_asset = {
                    "name": uploaded_file.name,
                    "type": uploaded_file.name.split('.')[-1].upper(),
                    "tags": [t.strip() for t in tags.split(',')],
                    "version": 1
                }
                st.session_state.assets.append(new_asset)
                st.success("Asset ingested and tagged successfully.")

    with col2:
        st.subheader("Asset Repository")
        for idx, asset in enumerate(st.session_state.assets):
            with st.container(border=True):
                c1, c2 = st.columns([3, 1])
                c1.markdown(f"📄 **{asset['name']}** (v{asset['version']})")
                c1.caption(f"Type: {asset['type']} | Tags: {', '.join(asset['tags'])}")
                c2.button("Download", key=f"dl_{idx}", use_container_width=True)

def render_ai_tools():
    st.header("AI Creative Tools")
    st.caption("Powered by Groq & Llama 3.1 70B")
    
    tab1, tab2, tab3 = st.tabs(["Storyboard Generator", "Scene Enhancement", "Production Optimizer"])
    
    with tab1:
        script = st.text_area("Paste Script or Treatment here:", height=200)
        if st.button("Generate Storyboard Breakdown"):
            if script:
                with st.spinner("Processing via Groq..."):
                    result = ai_generate_storyboard(script)
                    st.markdown(result)
            else:
                st.warning("Please enter a script.")

    with tab2:
        scene = st.text_area("Describe the technical scene setup (e.g., polycount, lighting setup, physics sim):", height=150)
        if st.button("Analyze Scene Risks"):
            if scene:
                with st.spinner("Supervising scene parameters..."):
                    result = ai_analyze_scene(scene)
                    st.info(result)

    with tab3:
        project_names = st.session_state.projects['name'].tolist()
        selected_proj = st.selectbox("Select Project for AI Audit", project_names)
        if st.button("Run Executive Audit"):
            proj_data = st.session_state.projects[st.session_state.projects['name'] == selected_proj].to_dict('records')[0]
            with st.spinner("Running deep analytical audit..."):
                result = ai_optimize_production(str(proj_data))
                st.success(result)

def render_collaboration():
    st.header("Project Collaboration")
    
    project_names = st.session_state.projects['name'].tolist()
    selected_proj = st.selectbox("Project Thread", project_names)
    
    st.divider()
    
    proj_comments = [c for c in st.session_state.comments if c['project'] == selected_proj]
    if not proj_comments:
        st.info("No comments yet. Start the discussion.")
    else:
        for c in proj_comments:
            with st.chat_message(name="user" if c['author'] == "Artist" else "assistant"):
                st.markdown(f"**{c['author']}** <span style='color:gray;font-size:0.8em;'>at {c['time']}</span>", unsafe_allow_html=True)
                st.write(c['text'])
                
    st.divider()
    new_comment = st.chat_input("Add a production note...")
    if new_comment:
        st.session_state.comments.append({
            "project": selected_proj,
            "author": st.session_state.user["role"],
            "text": new_comment,
            "time": datetime.now().strftime("%I:%M %p")
        })
        st.rerun()

def render_analytics():
    st.header("Studio Analytics")
    df = st.session_state.projects
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("Budget Burn Rate")
        for _, row in df.iterrows():
            pct = int((row['spent'] / row['budget']) * 100) if row['budget'] > 0 else 0
            st.markdown(f"**{row['name']}**")
            st.progress(pct / 100, text=f"{pct}% utilized")
            
    with col2:
        st.subheader("Timeline Analysis")
        delay_data = df[df['status'] == 'Delayed']
        if not delay_data.empty:
            st.error(f"Warning: {len(delay_data)} project(s) are currently flagged as delayed.")
            st.dataframe(delay_data[['name', 'deadline', 'stage']], hide_index=True)
        else:
            st.success("All projects are currently on schedule.")
            
        st.subheader("AI System Usage")
        st.metric("Groq API Calls (Session)", "12", delta="+3")

# ==========================================
# 5. MAIN APPLICATION ROUTER
# ==========================================
def main():
    init_mock_data()
    
    if not check_auth():
        login_ui()
        return

    with st.sidebar:
        st.title("🎬 StudioFlow")
        st.caption(f"Logged in as: **{st.session_state.user['name']}** ({st.session_state.user['role']})")
        st.divider()
        
        menu = ["Executive Dashboard", "Projects", "Asset Management", "AI Creative Tools", "Collaboration", "Analytics"]
        choice = st.radio("Navigation", menu, label_visibility="collapsed")
        
        st.divider()
        if st.button("Logout", use_container_width=True):
            logout()

    # Routing logic
    if choice == "Executive Dashboard":
        render_dashboard()
    elif choice == "Projects":
        render_projects()
    elif choice == "Asset Management":
        render_assets()
    elif choice == "AI Creative Tools":
        render_ai_tools()
    elif choice == "Collaboration":
        render_collaboration()
    elif choice == "Analytics":
        render_analytics()

if __name__ == "__main__":
    main()
