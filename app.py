# app.py (Hackathon Ready - Interactive & Stylish Version)
import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime
import json
from gtts import gTTS
import base64
import time
import numpy as np

from enhanced_mood_detector import MoodDetector, ReplyGenerator
from lead_utils import get_lead_warmth_score, generate_lead_summary, suggest_next_action, save_lead_to_csv
from revenue_insights import compute_revenue_summary

from auth import hash_password, validate_user, save_user, user_exists
import streamlit as st
import re
import webbrowser
import threading
from telegram_bot import start_bot
from daily_trending_sales import render_daily_trending_section

@st.cache_resource
def launch_telegram_bot():
    bot_thread = threading.Thread(target=start_bot, daemon=True)
    bot_thread.start()
    return "Bot running"

launch_telegram_bot()  # Run the bot when Streamlit starts



# Initialize session state
if "logged_in" not in st.session_state:
    st.session_state.logged_in = False
if "username" not in st.session_state:
    st.session_state.username = ""
if "theme" not in st.session_state:
    st.session_state.theme = "dark"
if "animations_enabled" not in st.session_state:
    st.session_state.animations_enabled = True

def logout():
    """Handle user logout with smooth animation"""
    with st.spinner("Logging out..."):
        time.sleep(1)
        st.session_state.logged_in = False
        st.session_state.username = ""
        # Clear all session data
        for key in ['chat_history', 'analytics_data', 'mood_detector', 'reply_generator']:
            if key in st.session_state:
                if key in ['mood_detector', 'reply_generator']:
                    del st.session_state[key]
                else:
                    st.session_state[key] = []
    st.success("🚀 Logged out successfully!")
    time.sleep(0.5)
    st.rerun()

def show_login():
    """Modern login interface with animations"""
    st.markdown("""
    <div style="text-align: center; padding: 2rem 0;">
        <h1 style="
            font-size: 3.5rem;
            font-weight: 800;
            margin-bottom: 0.5rem;
            white-space: nowrap;
            animation: glow 2s ease-in-out infinite alternate;
        ">
            <span style="color: #8ab4f8;">🧠</span>&nbsp;
            <span style="
                background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
                -webkit-background-clip: text;
                -webkit-text-fill-color: transparent;
            ">Smart Sales Agent Pro</span>
        </h1>
        <p style="font-size: 1.2rem; color: #aaa; margin-top: 0.5rem;">
            AI-Powered Customer Emotion Detection & Smart Reply Generation
        </p>
    </div>
    """, unsafe_allow_html=True)



    # Centering the login form
    col1, col2, col3 = st.columns([1, 2, 1])
    
    with col2:
        with st.container():
            st.markdown("""
            <div style="
                background: linear-gradient(135deg, rgba(255,255,255,0.1) 0%, rgba(255,255,255,0.05) 100%);
                backdrop-filter: blur(10px);
                border-radius: 20px;
                padding: 0rem;
                border: 1px solid rgba(255,255,255,0.1);
                box-shadow: 0 20px 40px rgba(0,0,0,0.1);
            ">
            """, unsafe_allow_html=True)
            
            tab1, tab2 = st.tabs(["🔑 Login", "📝 Sign Up"])

            with tab1:
                st.markdown("### Welcome Back!")
                uname = st.text_input("Username", placeholder="Enter your username")
                passwd = st.text_input("Password", type="password", placeholder="Enter your password")
                
                if st.button("🚀 Login", type="primary", use_container_width=True):
                    if validate_user(uname, passwd):
                        with st.spinner("Authenticating..."):
                            time.sleep(1)
                            st.session_state.logged_in = True
                            st.session_state.username = uname
                            st.success(f"🎉 Welcome back, {uname}!")
                            st.balloons()
                            time.sleep(1)
                            st.rerun()
                    else:
                        st.error("❌ Invalid credentials. Please try again.")

            with tab2:
                st.markdown("### Join Us!")
                new_uname = st.text_input("Choose Username", placeholder="Pick a unique username")
                new_passwd = st.text_input("Create Password", type="password", placeholder="Create a strong password")
                
                if st.button("🌟 Create Account", type="primary", use_container_width=True):
                    if user_exists(new_uname):
                        st.warning("⚠ Username already taken. Try another one!")
                    else:
                        with st.spinner("Creating your account..."):
                            time.sleep(1)
                            hashed_pw = hash_password(new_passwd)
                            save_user(new_uname, hashed_pw)
                            st.success("🎊 Account created successfully! Please login.")
                            st.balloons()
            
            st.markdown("</div>", unsafe_allow_html=True)

# Check if user is logged in
if not st.session_state.logged_in:
    show_login()
    st.stop()

# Page configuration
st.set_page_config(
    page_title="Smart Sales Agent Pro", 
    page_icon="🧠", 
    layout="wide",
    initial_sidebar_state="expanded"
)

# Advanced Custom CSS with animations and modern design
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700;800&display=swap');
    
    /* Global Styles */
    * {
        font-family: 'Inter', sans-serif;
    }
    
    /* Animations */
    @keyframes glow {
        from { text-shadow: 0 0 20px rgba(102, 126, 234, 0.5); }
        to { text-shadow: 0 0 30px rgba(102, 126, 234, 0.8); }
    }
    
    @keyframes fadeInUp {
        from { opacity: 0; transform: translateY(30px); }
        to { opacity: 1; transform: translateY(0); }
    }
    
    @keyframes pulse {
        0%, 100% { transform: scale(1); }
        50% { transform: scale(1.05); }
    }
    
    @keyframes slideIn {
        from { transform: translateX(-100%); opacity: 0; }
        to { transform: translateX(0); opacity: 1; }
    }
    
    /* Main Container */
    .main .block-container {
        padding-top: 2rem;
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        min-height: 100vh;
    }
    
    /* Header Styling */
    .main-header {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        font-size: 3.5rem;
        font-weight: 800;
        text-align: center;
        margin-bottom: 2rem;
        animation: glow 3s ease-in-out infinite alternate;
    }
    
    /* Glass Card Effect */
    .glass-card {
        background: rgba(255, 255, 255, 0.1);
        backdrop-filter: blur(15px);
        border-radius: 20px;
        padding: 2rem;
        border: 1px solid rgba(255, 255, 255, 0.2);
        box-shadow: 0 25px 50px rgba(0, 0, 0, 0.1);
        animation: fadeInUp 0.6s ease-out;
        margin-bottom: 2rem;
    }
    
    /* User Info Card */
    .user-info {
        background: linear-gradient(135deg, rgba(255,255,255,0.2) 0%, rgba(255,255,255,0.1) 100%);
        backdrop-filter: blur(10px);
        padding: 1rem 1.5rem;
        border-radius: 15px;
        border: 1px solid rgba(255,255,255,0.2);
        color: white;
        animation: slideIn 0.8s ease-out;
    }
    
    /* Mood Display */
    .mood-display {
        background: linear-gradient(135deg, #ff6b6b 0%, #ee5a24 100%);
        color: white;
        font-size: 1.3rem;
        font-weight: 600;
        padding: 2rem;
        border-radius: 20px;
        margin: 1rem 0;
        text-align: center;
        box-shadow: 0 15px 30px rgba(255, 107, 107, 0.3);
        animation: pulse 2s infinite;
    }
    
    /* Reply Box */
    .reply-box {
        background: linear-gradient(135deg, #74b9ff 0%, #0984e3 100%);
        color: white;
        padding: 2rem;
        border-radius: 20px;
        margin: 1rem 0;
        box-shadow: 0 15px 30px rgba(116, 185, 255, 0.3);
        animation: fadeInUp 0.8s ease-out;
    }
    
    /* Stats Boxes */
    .stats-box {
        background: linear-gradient(135deg, rgba(255,255,255,0.15) 0%, rgba(255,255,255,0.05) 100%);
        backdrop-filter: blur(10px);
        padding: 1.5rem;
        border-radius: 15px;
        border: 1px solid rgba(255,255,255,0.1);
        margin: 1rem 0;
        transition: all 0.3s ease;
        color: white;
    }
    
    .stats-box:hover {
        transform: translateY(-5px);
        box-shadow: 0 20px 40px rgba(0,0,0,0.2);
    }
    
    /* Alert Styles */
    .alert-danger {
        background: linear-gradient(135deg, #ff6b6b 0%, #ee5a24 100%);
        color: white;
        padding: 1rem 2rem;
        border-radius: 15px;
        border: none;
        animation: pulse 1s infinite;
        font-weight: 600;
    }
    
    .alert-success {
        background: linear-gradient(135deg, #00b894 0%, #00a085 100%);
        color: white;
        padding: 1rem 2rem;
        border-radius: 15px;
        border: none;
        font-weight: 600;
    }
    
    /* Button Styles */
    .stButton > button {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        color: white;
        border: none;
        border-radius: 25px;
        padding: 0.7rem 2rem;
        font-weight: 600;
        transition: all 0.3s ease;
        box-shadow: 0 10px 25px rgba(102, 126, 234, 0.3);
    }
    
    .stButton > button:hover {
        transform: translateY(-3px);
        box-shadow: 0 15px 35px rgba(102, 126, 234, 0.4);
    }
    
    /* Sidebar Styling */
    .css-1d391kg {
        background: linear-gradient(180deg, #667eea 0%, #764ba2 100%);
    }
    
    /* Progress Bar */
    .stProgress .st-bo {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        border-radius: 10px;
    }
    
    /* Chat History */
    .chat-item {
        background: rgba(255, 255, 255, 0.1);
        backdrop-filter: blur(10px);
        border-radius: 15px;
        padding: 1rem;
        margin: 0.5rem 0;
        border: 1px solid rgba(255, 255, 255, 0.1);
        transition: all 0.3s ease;
    }
    
    .chat-item:hover {
        transform: translateX(10px);
        box-shadow: 0 10px 25px rgba(0, 0, 0, 0.15);
    }
    
    /* Floating Action Button */
    .floating-btn {
        position: fixed;
        bottom: 30px;
        right: 30px;
        width: 60px;
        height: 60px;
        border-radius: 50%;
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        border: none;
        color: white;
        font-size: 1.5rem;
        box-shadow: 0 10px 25px rgba(102, 126, 234, 0.4);
        cursor: pointer;
        transition: all 0.3s ease;
        z-index: 1000;
    }
    
    .floating-btn:hover {
        transform: scale(1.1);
        box-shadow: 0 15px 35px rgba(102, 126, 234, 0.6);
    }
    
    /* Text Area Styling */
    .stTextArea textarea {
        background: rgba(255, 255, 255, 0.1);
        border: 1px solid rgba(255, 255, 255, 0.2);
        border-radius: 15px;
        color: white;
        backdrop-filter: blur(10px);
    }
    
    .stTextArea textarea:focus {
        border-color: #667eea;
        box-shadow: 0 0 25px rgba(102, 126, 234, 0.3);
    }
    
    /* Tabs */
    .stTabs [data-baseweb="tab-list"] {
        background: rgba(255, 255, 255, 0.1);
        border-radius: 15px;
        padding: 0.5rem;
    }
    
    .stTabs [data-baseweb="tab"] {
        background: transparent;
        border-radius: 10px;
        color: white;
        font-weight: 600;
    }
    
    .stTabs [aria-selected="true"] {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
    }
    
    /* Expander */
    .streamlit-expanderHeader {
        background: rgba(255, 255, 255, 0.1);
        border-radius: 15px;
        border: 1px solid rgba(255, 255, 255, 0.2);
        color: white;
        font-weight: 600;
    }
    
    /* Metrics */
    .metric-card {
        background: linear-gradient(135deg, rgba(255,255,255,0.15) 0%, rgba(255,255,255,0.05) 100%);
        backdrop-filter: blur(10px);
        padding: 1.5rem;
        border-radius: 15px;
        border: 1px solid rgba(255,255,255,0.1);
        text-align: center;
        transition: all 0.3s ease;
        color: white;
    }
    
    .metric-card:hover {
        transform: translateY(-5px);
        box-shadow: 0 20px 40px rgba(0,0,0,0.2);
    }
    
    /* Loading Animation */
    .loading-container {
        display: flex;
        justify-content: center;
        align-items: center;
        height: 100px;
    }
    
    .loading-spinner {
        width: 40px;
        height: 40px;
        border: 4px solid rgba(255,255,255,0.3);
        border-top: 4px solid #667eea;
        border-radius: 50%;
        animation: spin 1s linear infinite;
    }
    
    @keyframes spin {
        0% { transform: rotate(0deg); }
        100% { transform: rotate(360deg); }
    }
</style>
""", unsafe_allow_html=True)

# Header with glassmorphism effect
st.markdown("""
<div class="glass-card" style="padding: 20px;">
    <div style="text-align: center;">
        <span style="font-size: 2.5rem;">
            <span style="color: #8ab4f8;">🧠</span> 
            <span class="main-header" style="font-size: 2.5rem; font-weight: bold; color: #a287ff; text-shadow: 0 0 10px #a287ff;">
                Smart Sales Agent Pro
            </span>
        </span>
    </div>
    <div style="text-align: center; color: white; font-size: 1.2rem; margin-top: -0.5rem;">
        AI-Powered Customer Emotion Detection & Smart Reply Generation
    </div>
</div>
""", unsafe_allow_html=True)


# Top Navigation Bar
col_nav1, col_nav2, col_nav3, col_nav4 = st.columns([2, 1, 1, 1])

with col_nav1:
    st.markdown(f"""
    <div class="user-info">
        <span style="font-size: 1.1rem;">👤 Welcome, <strong>{st.session_state.username}</strong></span>
        <br><span style="font-size: 0.9rem; opacity: 0.8;">🚀 Ready to analyze customer emotions!</span>
    </div>
    """, unsafe_allow_html=True)

with col_nav2:
    if st.button("🌙 Dark Mode", key="theme_toggle"):
        st.session_state.theme = "light" if st.session_state.theme == "dark" else "dark"
        st.rerun()

with col_nav3:
    if st.button("✨ Effects", key="effects_toggle"):
        st.session_state.animations_enabled = not st.session_state.animations_enabled
        st.rerun()

with col_nav4:
    if st.button("🚪 Logout", key="logout_btn"):
        logout()

# Session Initialization
if 'mood_detector' not in st.session_state:
    st.session_state.mood_detector = MoodDetector()
if 'reply_generator' not in st.session_state:
    st.session_state.reply_generator = ReplyGenerator()
if 'chat_history' not in st.session_state:
    st.session_state.chat_history = []
if 'analytics_data' not in st.session_state:
    st.session_state.analytics_data = []

# Enhanced Sidebar with modern design
st.sidebar.markdown("""
<div style="text-align: center; padding: 1rem; background: rgba(255,255,255,0.1); border-radius: 15px; margin-bottom: 2rem;">
    <h2 style="color: white; margin: 0;">🛠 Control Center</h2>
    <p style="color: rgba(255,255,255,0.8); margin: 0.5rem 0 0 0;">Customize your experience</p>
</div>
""", unsafe_allow_html=True)

# Advanced Settings
st.sidebar.markdown("### ⚙ Advanced Settings")
show_scores = st.sidebar.checkbox("📊 Show Raw Emotion Scores", True)
show_intensity = st.sidebar.checkbox("🔥 Show Emotion Intensity", True)
show_history = st.sidebar.checkbox("📜 Show Chat History", True)
show_analytics = st.sidebar.checkbox("📈 Show Analytics Dashboard", True)
auto_speak = st.sidebar.checkbox("🔊 Auto-speak results", False)
# Daily Trends Toggle Section
st.sidebar.markdown("### 📅 Daily Insights")
show_daily_trends = st.sidebar.checkbox("📈 Show Daily Sales Trends", True)

if show_daily_trends:
    render_daily_trending_section()



# Real-time Stats
if st.session_state.analytics_data:
    st.sidebar.markdown("### 📊 Live Statistics")
    total = len(st.session_state.analytics_data)
    moods = [item['Mood Category'] for item in st.session_state.analytics_data]
    common_mood = max(set(moods), key=moods.count) if moods else "N/A"
    confidences = [item['Confidence'] for item in st.session_state.analytics_data]
    avg_conf = sum(confidences) / len(confidences) if confidences else 0
    
    # Animated metric cards
    st.sidebar.markdown(f"""
    <div class="metric-card">
        <h3 style="margin: 0; color: #667eea;">📝 {total}</h3>
        <p style="margin: 0.5rem 0 0 0; opacity: 0.9;">Total Messages</p>
    </div>
    """, unsafe_allow_html=True)
    
    st.sidebar.markdown(f"""
    <div class="metric-card">
        <h3 style="margin: 0; color: #667eea;">🎯 {common_mood}</h3>
        <p style="margin: 0.5rem 0 0 0; opacity: 0.9;">Common Mood</p>
    </div>
    """, unsafe_allow_html=True)
    
    st.sidebar.markdown(f"""
    <div class="metric-card">
        <h3 style="margin: 0; color: #667eea;">📈 {avg_conf:.1f}%</h3>
        <p style="margin: 0.5rem 0 0 0; opacity: 0.9;">Avg Confidence</p>
    </div>
    """, unsafe_allow_html=True)

# Telegram Integration
st.sidebar.markdown("---")
st.sidebar.markdown("### 💬 Telegram Integration")
telegram_bot_link = "https://t.me/smartsales_pro_bot"

if st.sidebar.button("📲 Launch Telegram Bot", use_container_width=True):
    # Method 1: JavaScript redirect (more reliable in web environment)
    st.sidebar.markdown(f"""
    <script>
    window.open('{telegram_bot_link}', '_blank');
    </script>
    """, unsafe_allow_html=True)
    
    # Method 2: Clickable link as backup
    st.sidebar.markdown(f"""
    <a href="{telegram_bot_link}" target="_blank" style="
        display: inline-block;
        padding: 10px 20px;
        background-color: #0088cc;
        color: white;
        text-decoration: none;
        border-radius: 5px;
        margin-top: 10px;
    ">🚀 Click here if bot didn't open automatically</a>
    """, unsafe_allow_html=True)
    
    st.sidebar.success("🚀 Telegram bot launched!")

# Main Content Area
st.markdown("""
<div style="margin-top: 25px;">
<div class="glass-card">
    <h2 style="color: white; text-align: center; margin-bottom: 2rem;">
        🎯 Customer Message Analysis Center
    </h2>
</div>
""", unsafe_allow_html=True)

# Input Section with enhanced design
col1, col2 = st.columns([3, 1])

with col1:
    st.markdown("""
    <div class="glass-card">
        <h3 style="color: white; margin-bottom: 1rem;">📩 Customer Message Input</h3>
    </div>
    """, unsafe_allow_html=True)
    
    default_input = st.session_state.get("test_input", "")
    user_input = st.text_area(
        "Enter the customer's message:",
        height=120,
        value=default_input,
        key="main_input",
        placeholder="Paste or type the customer's message here to analyze their emotions and generate smart replies..."
    )

with col2:
    st.markdown("""
    <div class="glass-card">
        <h3 style="color: white; margin-bottom: 1rem;">🎭 Quick Test Messages</h3>
    </div>
    """, unsafe_allow_html=True)
    
    test_messages = {
        "😊 Excited": "Hey! I'm really excited about your new product launch! This looks amazing!",
        "😠 Angry": "This is absolutely terrible service! I'm furious and want my money back right now!",
        "😞 Disappointed": "I'm really disappointed with my recent experience. Expected much better.",
        "😕 Confused": "I've been trying to reach someone for hours and no one is responding. What's going on?",
        "❤ Happy": "This is incredible! I love what you guys are doing. Keep up the great work!",
        "💰 Price Inquiry": "Can you tell me about your pricing plans? I'm interested in the premium features.",
        "🔥 Urgent": "URGENT: I need help immediately! My account has been compromised!",
        "🤔 Curious": "I'm curious about how this works. Can you explain the process to me?"
    }

    for label, msg in test_messages.items():
        if st.button(label, key=f"test_{label}", use_container_width=True):
            st.session_state.test_input = msg
            st.rerun()

# Enhanced Analysis Button
st.markdown("<br>", unsafe_allow_html=True)
col_btn1, col_btn2, col_btn3 = st.columns([1, 2, 1])

with col_btn2:
    if st.button("🧠 Analyze Customer Emotion & Generate Smart Reply", type="primary", use_container_width=True) and user_input:
        # Enhanced progress tracking
        progress_container = st.container()
        
        with progress_container:
            st.markdown("""
            <div class="loading-container">
                <div class="loading-spinner"></div>
            </div>
            """, unsafe_allow_html=True)
            
            progress = st.progress(0)
            status = st.empty()
            
            # Step 1: Mood Detection
            status.markdown("🔍 *Step 1:* Analyzing customer emotions...")
            progress.progress(20)
            time.sleep(0.8)
            
            try:
                mood_result = st.session_state.mood_detector.detect_mood(user_input)
                mood = mood_result['mood']
                confidence = mood_result['confidence']
                raw_scores = mood_result['raw_scores']
                label = mood_result['label']
                mood_category = st.session_state.mood_detector.get_mood_category(label)
                intensity = st.session_state.mood_detector.analyze_sentiment_intensity(user_input)
                
                # Step 2: Reply Generation
                status.markdown("💬 *Step 2:* Generating intelligent reply...")
                progress.progress(50)
                time.sleep(0.8)
                
                reply = st.session_state.reply_generator.generate_reply(user_input, mood_category, intensity)
                
                # Step 3: Lead Analysis
                status.markdown("📊 *Step 3:* Computing lead analysis...")
                progress.progress(80)
                time.sleep(0.8)
                
                lead_score = get_lead_warmth_score(mood_category, intensity)
                summary = generate_lead_summary(user_input)
                next_action = suggest_next_action(summary)
                
                progress.progress(100)
                status.markdown("✅ *Analysis Complete!* Results ready below.")
                
                # Clear progress after delay
                time.sleep(1)
                progress.empty()
                status.empty()
                
                # Enhanced Alert System
                mood_text = re.sub(r'[^\w\s]', '', mood).lower().strip()
                negative_moods = [
                    "angry", "sad", "disappointed", "fearful", "frustrated", "upset",
                    "annoyed", "unhappy", "rude", "agitated", "depressed", "anxious"
                ]
                
                if mood_text in negative_moods:
                    st.markdown(f"""
                    <div class="alert-danger">
                        🚨 <strong>URGENT ALERT:</strong> Customer appears <strong>{mood_text}</strong>! 
                        Immediate attention required to prevent escalation.
                    </div>
                    """, unsafe_allow_html=True)
                    if st.session_state.animations_enabled:
                        st.balloons()
                else:
                    st.markdown(f"""
                    <div class="alert-success">
                        ✅ <strong>POSITIVE SIGNAL:</strong> Customer seems <strong>{mood}</strong>. 
                        Great opportunity for engagement!
                    </div>
                    """, unsafe_allow_html=True)
                
                # Save lead data
                lead = {
                    "Timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                    "Message": user_input,
                    "Mood": mood,
                    "Mood Category": mood_category,
                    "Confidence": confidence,
                    "Intensity": intensity,
                    "Reply": reply,
                    "Lead Score": lead_score,
                    "Summary": summary,
                    "Suggested Action": next_action
                }
                save_lead_to_csv(lead)
                
                # Enhanced Results Display
                st.markdown("---")
                
                # Results in beautiful cards
                result_col1, result_col2 = st.columns(2)
                
                with result_col1:
                    st.markdown(f"""
                    <div class="glass-card">
                        <h3 style="color: white; text-align: center; margin-bottom: 1.5rem;">
                            🧠 Emotion Analysis Results
                        </h3>
                        <div class="mood-display">
                            <div style="font-size: 2rem; margin-bottom: 0.5rem;">{mood}</div>
                            <div style="font-size: 1rem; opacity: 0.9;">
                                Confidence: {confidence}% | Category: {mood_category.title()}
                            </div>
                            {f'<div style="font-size: 1rem; opacity: 0.9; margin-top: 0.5rem;">Intensity: {intensity.title()}</div>' if show_intensity else ''}
                        </div>
                    </div>
                    """, unsafe_allow_html=True)
                    
                    # Raw scores visualization
                    if show_scores and raw_scores:
                        df = pd.DataFrame(list(raw_scores.items()), columns=["Emotion", "Score"]).sort_values(by="Score", ascending=False)
                        fig = px.bar(
                            df.head(6), 
                            x="Score", 
                            y="Emotion", 
                            orientation='h',
                            title="Emotion Breakdown",
                            color="Score",
                            color_continuous_scale="Viridis"
                        )
                        fig.update_layout(
                            plot_bgcolor='rgba(0,0,0,0)',
                            paper_bgcolor='rgba(0,0,0,0)',
                            font_color='white'
                        )
                        st.plotly_chart(fig, use_container_width=True)
                
                with result_col2:
                    st.markdown(f"""
                    <div class="glass-card">
                        <h3 style="color: white; text-align: center; margin-bottom: 1.5rem;">
                            🤖 AI-Generated Smart Reply
                        </h3>
                        <div class="reply-box">
                            <div style="font-size: 1.1rem; line-height: 1.6;">
                                {reply}
                            </div>
                        </div>
                        <div style="margin-top: 1rem; text-align: center;">
                            <small style="color: rgba(255,255,255,0.8);">
                                💡 Lead Score: {lead_score}/100 | Action: {next_action}
                            </small>
                        </div>
                    </div>
                    """, unsafe_allow_html=True)
                
                # Auto-speak feature
                if auto_speak:
                    tts_text = f"Customer mood detected as {mood} with {confidence}% confidence. {reply}"
                    try:
                        tts = gTTS(tts_text)
                        tts.save("analysis_result.mp3")
                        
                        with open("analysis_result.mp3", "rb") as f:
                            audio_bytes = f.read()
                            b64 = base64.b64encode(audio_bytes).decode()
                            st.markdown(f"""
                            <audio controls autoplay>
                                <source src="data:audio/mp3;base64,{b64}" type="audio/mp3">
                            </audio>
                            """, unsafe_allow_html=True)
                    except Exception as e:
                        st.warning(f"🔊 Audio generation failed: {e}")
                
                # Update session data
                st.session_state.chat_history.append(lead)
                st.session_state.analytics_data.append(lead)
                
                # Success animation
                if st.session_state.animations_enabled:
                    st.success("🎉 Analysis completed successfully!")
                    
            except Exception as e:
                st.error(f"⚠ Analysis failed: {str(e)}")
                progress.empty()
                status.empty()

# Enhanced Analytics Dashboard
if show_analytics and st.session_state.analytics_data:
    st.markdown("---")
    st.markdown("""
    <div class="glass-card">
        <h2 style="color: white; text-align: center; margin-bottom: 2rem;">
            📊 Advanced Analytics Dashboard
        </h2>
    </div>
    """, unsafe_allow_html=True)
    
    # Revenue Analysis Section
    with st.expander("💰 Revenue Impact Analysis", expanded=True):
        revenue_data = compute_revenue_summary()
        
        # Key metrics in a beautiful grid
        metric_col1, metric_col2, metric_col3, metric_col4 = st.columns(4)
        
        with metric_col1:
            st.markdown(f"""
            <div class="metric-card">
                <h2 style="margin: 0; color: #00b894;">₹{revenue_data['actual_revenue']:,}</h2>
                <p style="margin: 0.5rem 0 0 0; opacity: 0.9;">Actual Revenue</p>
            </div>
            """, unsafe_allow_html=True)
        
        with metric_col2:
            st.markdown(f"""
            <div class="metric-card">
                <h2 style="margin: 0; color: #fdcb6e;">₹{revenue_data['projected_revenue']:,}</h2>
                <p style="margin: 0.5rem 0 0 0; opacity: 0.9;">Projected Revenue</p>
            </div>
            """, unsafe_allow_html=True)
        
        with metric_col3:
            st.markdown(f"""
            <div class="metric-card">
                <h2 style="margin: 0; color: #e17055;">{revenue_data['hot_count']}</h2>
                <p style="margin: 0.5rem 0 0 0; opacity: 0.9;">🔥 Hot Leads</p>
            </div>
            """, unsafe_allow_html=True)
        
        with metric_col4:
            st.markdown(f"""
            <div class="metric-card">
                <h2 style="margin: 0; color: #74b9ff;">{revenue_data['warm_count']}</h2>
                <p style="margin: 0.5rem 0 0 0; opacity: 0.9;">🟠 Warm Leads</p>
            </div>
            """, unsafe_allow_html=True)
            
        
        
        
        # AI-Powered Voice Summary
        st.markdown("### 🎙 AI Voice Summary")
        hot = revenue_data['hot_count']
        warm = revenue_data['warm_count']
        cold = revenue_data['cold_count']
        projected = revenue_data['projected_revenue']
        actual = revenue_data['actual_revenue']
        
        if hot > 0:
            suggestion = f"Priority action: Close {hot} hot lead{'s' if hot > 1 else ''} immediately for maximum revenue impact."
        elif warm > 0:
            suggestion = f"Focus on converting {warm} warm lead{'s' if warm > 1 else ''} to hot leads."
        else:
            suggestion = "Generate new leads through targeted marketing campaigns."
        
        summary_text = (
            f"Sales Intelligence Report: {suggestion} "
            f"Current projected revenue stands at ₹{projected:,} with actual adjusted revenue of ₹{actual:,}. "
            f"Lead distribution: {hot} hot, {warm} warm, and {cold} cold leads. "
            f"Recommended immediate action: {suggestion}"
        )
        
        voice_col1, voice_col2 = st.columns([3, 1])
        
        with voice_col1:
            st.markdown(f"""
            <div class="glass-card">
                <h4 style="color: white; margin-bottom: 1rem;">🤖 AI Insights</h4>
                <p style="color: rgba(255,255,255,0.9); line-height: 1.6;">
                    {summary_text}
                </p>
            </div>
            """, unsafe_allow_html=True)
        
        with voice_col2:
            if st.button("🔊 Play AI Summary", use_container_width=True):
                try:
                    with st.spinner("🎙 Generating voice summary..."):
                        tts = gTTS(summary_text)
                        tts.save("dashboard_summary.mp3")
                        
                        with open("dashboard_summary.mp3", "rb") as f:
                            audio_bytes = f.read()
                            b64 = base64.b64encode(audio_bytes).decode()
                            st.markdown(f"""
                            <audio controls autoplay>
                                <source src="data:audio/mp3;base64,{b64}" type="audio/mp3">
                            </audio>
                            """, unsafe_allow_html=True)
                        st.success("🎵 Voice summary ready!")
                except Exception as e:
                    st.error(f"🔊 Voice generation failed: {e}")
        
        # Enhanced Visualizations
        df_plot = revenue_data['dataframe']
        
        if not df_plot.empty:
            chart_col1, chart_col2 = st.columns(2)
            
            with chart_col1:
                # 3D Revenue Chart
                revenue_by_type = df_plot.groupby("lead_type")["estimated_revenue"].sum().reset_index()
                revenue_by_type["lead_type"] = revenue_by_type["lead_type"].str.title()
                
                fig_3d = px.bar(
                    revenue_by_type, 
                    x="lead_type", 
                    y="estimated_revenue",
                    title="💰 Revenue by Lead Type",
                    labels={"lead_type": "Lead Type", "estimated_revenue": "Revenue (₹)"},
                    color="estimated_revenue",
                    color_continuous_scale="Viridis",
                    text="estimated_revenue"
                )
                fig_3d.update_traces(texttemplate='₹%{text:,.0f}', textposition='outside')
                fig_3d.update_layout(
                    plot_bgcolor='rgba(0,0,0,0)',
                    paper_bgcolor='rgba(0,0,0,0)',
                    font_color='white',
                    title_font_size=16
                )
                st.plotly_chart(fig_3d, use_container_width=True)
            
            with chart_col2:
                # Interactive Donut Chart
                lead_counts = [revenue_data['hot_count'], revenue_data['warm_count'], revenue_data['cold_count']]
                lead_labels = ['🔥 Hot', '🟠 Warm', '❄ Cold']
                colors = ['#e17055', '#fdcb6e', '#74b9ff']
                
                fig_donut = go.Figure(data=[go.Pie(
                    labels=lead_labels, 
                    values=lead_counts, 
                    hole=0.5,
                    marker_colors=colors,
                    textinfo='label+percent',
                    textfont_size=12
                )])
                fig_donut.update_layout(
                    title="🎯 Lead Distribution",
                    plot_bgcolor='rgba(0,0,0,0)',
                    paper_bgcolor='rgba(0,0,0,0)',
                    font_color='white',
                    title_font_size=16
                )
                st.plotly_chart(fig_donut, use_container_width=True)
            
            # Time Series Analysis
            if len(df_plot) > 1:
                df_plot['timestamp'] = pd.to_datetime(df_plot['Timestamp'])
                df_plot = df_plot.sort_values('timestamp')
                
                fig_timeline = px.line(
                    df_plot, 
                    x='timestamp', 
                    y='estimated_revenue',
                    title="📈 Revenue Timeline",
                    markers=True,
                    color_discrete_sequence=['#667eea']
                )
                fig_timeline.update_layout(
                    plot_bgcolor='rgba(0,0,0,0)',
                    paper_bgcolor='rgba(0,0,0,0)',
                    font_color='white',
                    title_font_size=16
                )
                st.plotly_chart(fig_timeline, use_container_width=True)
            
            # Interactive Revenue Editor
            st.markdown("### ✏ Revenue Adjustment Center")
            with st.form("revenue_edit_form"):
                st.markdown("""
                <div class="glass-card">
                    <h4 style="color: white; margin-bottom: 1rem;">💰 Adjust Revenue Estimates</h4>
                    <p style="color: rgba(255,255,255,0.8); margin-bottom: 1rem;">
                        Fine-tune your revenue projections based on real-world insights
                    </p>
                </div>
                """, unsafe_allow_html=True)
                
                editable_df = df_plot[["Timestamp", "Message", "Lead Score", "estimated_revenue"]].copy()
                editable_df = editable_df.rename(columns={"estimated_revenue": "Revenue (₹)"})
                
                edited_df = st.data_editor(
                    editable_df, 
                    num_rows="dynamic", 
                    use_container_width=True,
                    key="editable_revenue",
                    column_config={
                        "Revenue (₹)": st.column_config.NumberColumn(
                            "Revenue (₹)",
                            help="Adjust the revenue estimate",
                            min_value=0,
                            max_value=1000000,
                            step=1000,
                            format="₹%d"
                        )
                    }
                )
                
                save_col1, save_col2 = st.columns([3, 1])
                with save_col2:
                    submitted = st.form_submit_button("💾 Save Changes", type="primary", use_container_width=True)
                
                if submitted:
                    with st.spinner("💾 Saving revenue adjustments..."):
                        for idx, row in edited_df.iterrows():
                            df_plot.at[idx, "estimated_revenue"] = row["Revenue (₹)"]
                        df_plot.to_csv("lead_data.csv", index=False)
                        time.sleep(1)
                        st.success("✅ Revenue estimates updated successfully!")
                        st.balloons()
        else:
            st.markdown("""
            <div class="glass-card">
                <div style="text-align: center; padding: 3rem; color: rgba(255,255,255,0.7);">
                    <h3>📊 No Data Available</h3>
                    <p>Start analyzing customer messages to see revenue insights!</p>
                </div>
            </div>
            """, unsafe_allow_html=True)

# Enhanced Conversation History
if show_history and st.session_state.chat_history:
    st.markdown("---")
    st.markdown("""
    <div class="glass-card">
        <h2 style="color: white; text-align: center; margin-bottom: 2rem;">
            💬 Conversation History & Insights
        </h2>
    </div>
    """, unsafe_allow_html=True)
    
    # Export options
    export_col1, export_col2, export_col3 = st.columns([2, 1, 1])
    
    with export_col1:
        st.markdown("### 📥 Export Options")
    
    with export_col2:
        json_data = json.dumps(st.session_state.chat_history, indent=2)
        st.download_button(
            "📊 Download JSON",
            data=json_data,
            file_name=f"sales_analysis_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json",
            mime="application/json"
        )
    
    with export_col3:
        if st.session_state.chat_history:
            csv_data = pd.DataFrame(st.session_state.chat_history).to_csv(index=False)
            st.download_button(
                "📋 Download CSV",
                data=csv_data,
                file_name=f"sales_analysis_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv",
                mime="text/csv"
            )
    
    # Advanced filtering
    st.markdown("### 🔍 Smart Filters")
    filter_col1, filter_col2, filter_col3 = st.columns(3)
    
    with filter_col1:
        mood_filter = st.selectbox(
            "Filter by Mood Category",
            ["All"] + list(set([item['Mood Category'] for item in st.session_state.chat_history])),
            key="mood_filter"
        )
    
    with filter_col2:
        intensity_filter = st.selectbox(
            "Filter by Intensity",
            ["All"] + list(set([item['Intensity'] for item in st.session_state.chat_history])),
            key="intensity_filter"
        )
    
    with filter_col3:
        confidence_filter = st.slider(
            "Min Confidence %",
            0, 100, 0,
            key="confidence_filter"
        )
    
    # Apply filters
    filtered_history = st.session_state.chat_history.copy()
    
    if mood_filter != "All":
        filtered_history = [item for item in filtered_history if item['Mood Category'] == mood_filter]
    
    if intensity_filter != "All":
        filtered_history = [item for item in filtered_history if item['Intensity'] == intensity_filter]
    
    filtered_history = [item for item in filtered_history if item['Confidence'] >= confidence_filter]
    
    # Display filtered results
    st.markdown(f"### 📋 Showing {len(filtered_history)} of {len(st.session_state.chat_history)} conversations")
    
    for i, item in enumerate(reversed(filtered_history[-10:])):  # Show last 10
        with st.expander(f"💬 #{len(filtered_history)-i} - {item['Timestamp']} - {item['Mood']} ({item['Confidence']}%)", expanded=False):
            conv_col1, conv_col2 = st.columns([2, 1])
            
            with conv_col1:
                st.markdown(f"""
                <div class="chat-item">
                    <h5 style="color: white; margin-bottom: 0.5rem;">📝 Customer Message</h5>
                    <p style="color: rgba(255,255,255,0.9); margin-bottom: 1rem;">{item['Message']}</p>
                    
                    <h5 style="color: white; margin-bottom: 0.5rem;">🤖 AI Response</h5>
                    <p style="color: rgba(255,255,255,0.9); background: rgba(102, 126, 234, 0.2); padding: 1rem; border-radius: 10px;">
                        {item['Reply']}
                    </p>
                </div>
                """, unsafe_allow_html=True)
            
            with conv_col2:
                st.markdown(f"""
                <div class="stats-box">
                    <h5 style="color: white; margin-bottom: 1rem;">📊 Analysis</h5>
                    <p><strong>Mood:</strong> {item['Mood']}</p>
                    <p><strong>Category:</strong> {item['Mood Category']}</p>
                    <p><strong>Confidence:</strong> {item['Confidence']}%</p>
                    <p><strong>Intensity:</strong> {item['Intensity']}</p>
                    <p><strong>Lead Score:</strong> {item['Lead Score']}/100</p>
                    <p><strong>Next Action:</strong> {item['Suggested Action']}</p>
                </div>
                """, unsafe_allow_html=True)

# Action Center
st.markdown("---")
st.markdown("""
<div class="glass-card">
    <h2 style="color: white; text-align: center; margin-bottom: 2rem;">
        🎯 Quick Actions Center
    </h2>
</div>
""", unsafe_allow_html=True)

action_col1, action_col2, action_col3, action_col4 = st.columns(4)

with action_col1:
    if st.button("🗑 Clear History", use_container_width=True):
        st.session_state.chat_history.clear()
        st.session_state.analytics_data.clear()
        st.success("🧹 History cleared!")
        st.rerun()

with action_col2:
    if st.button("📊 Export Analytics", use_container_width=True):
        if st.session_state.analytics_data:
            df = pd.DataFrame(st.session_state.analytics_data)
            csv = df.to_csv(index=False)
            st.download_button(
                "📥 Download Analytics",
                data=csv,
                file_name=f"analytics_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv",
                mime="text/csv"
            )
        else:
            st.warning("No analytics data available!")

with action_col3:
    if st.button("🔄 Refresh Data", use_container_width=True):
        st.rerun()

with action_col4:
    if st.button("🚀 Launch Demo", use_container_width=True):
        demo_messages = [
            "I'm extremely disappointed with your service!",
            "This is amazing! I love it!",
            "Can you help me understand the pricing?",
            "URGENT: I need immediate assistance!"
        ]
        for msg in demo_messages:
            st.session_state.test_input = msg
            st.success(f"Demo message loaded: {msg[:50]}...")
            break

# Footer with enhanced styling
st.markdown("---")
st.markdown(f"""
<div class="glass-card">
    <div style="text-align: center;">
        <h3 style="color: white; margin-bottom: 1rem;">🧠 Smart Sales Agent Pro</h3>
        <p style="color: rgba(255,255,255,0.8); margin-bottom: 1rem;">
            AI-Powered Customer Emotion Detection & Smart Reply Generation
        </p>
        <div style="display: flex; justify-content: center; gap: 2rem; margin-bottom: 1rem;">
            <div style="color: rgba(255,255,255,0.7);">
                👤 <strong>User:</strong> {st.session_state.username}
            </div>
            <div style="color: rgba(255,255,255,0.7);">
                📊 <strong>Messages:</strong> {len(st.session_state.chat_history)}
            </div>
            <div style="color: rgba(255,255,255,0.7);">
                🕒 <strong>Session:</strong> {datetime.now().strftime('%H:%M')}
            </div>
        </div>
        <p style="color: rgba(255,255,255,0.6); font-size: 0.9rem;">
            Built with ❤ for intelligent customer engagement
        </p>
    </div>
</div>
""", unsafe_allow_html=True)




