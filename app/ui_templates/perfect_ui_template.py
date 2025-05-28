"""Modern ChatGPT/Claude-style Streamlit UI for LUCA."""

import asyncio
import time
from datetime import datetime

import streamlit as st


def get_icon(name):
    """Return SVG path for minimalistic icons."""
    icons = {
        "chart": '<polyline points="22 12 18 12 15 21 9 3 6 12 2 12"></polyline>',
        "trending": '<polyline points="23 6 13.5 15.5 8.5 10.5 1 18"></polyline>',
        "flask": '<path d="M10 2v8L8 14c-1 2-1 4 0 6a5 5 0 0 0 8 0c1-2 1-4 0-6l-2-4V2"></path><path d="M8.5 2h7"></path><path d="M7 16h10"></path>',
        "target": '<circle cx="12" cy="12" r="10"></circle><circle cx="12" cy="12" r="6"></circle><circle cx="12" cy="12" r="2"></circle>',
    }
    return icons.get(name, "")


# Page config must be first
st.set_page_config(
    page_title="Luca - Quantitative Development Assistant",
    page_icon="L",
    layout="wide",
    initial_sidebar_state="expanded",
)

# Advanced CSS to make it look like ChatGPT/Claude
st.markdown(
    """
<style>
    /* Import Google Font */
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&display=swap');

    /* Hide Streamlit UI elements */
    #MainMenu {visibility: hidden;}
    header {visibility: hidden;}
    footer {visibility: hidden;}
    .stDeployButton {display: none;}

    /* Main app styling */
    .stApp {
        background-color: #FAFBFC;
        font-family: 'Inter', -apple-system, BlinkMacSystemFont, sans-serif;
    }

    /* Sidebar styling */
    section[data-testid="stSidebar"] {
        background-color: #FFFFFF;
        border-right: 1px solid #E5E7EB;
        width: 260px !important;
    }

    section[data-testid="stSidebar"] > div {
        padding: 1rem;
    }

    /* Chat container */
    .chat-container {
        max-width: 800px;
        margin: 0 auto;
        height: calc(100vh - 200px);
        overflow-y: auto;
        padding: 2rem;
    }

    /* Message styling */
    .user-message {
        background: linear-gradient(135deg, #8b5cf6 0%, #ec4899 100%);
        color: white;
        padding: 1rem 1.5rem;
        border-radius: 18px;
        margin: 1rem 0;
        max-width: 70%;
        margin-left: auto;
        box-shadow: 0 2px 15px rgba(139, 92, 246, 0.25);
    }

    .assistant-message {
        background: #F3F4F6;
        color: #1F2937;
        padding: 1rem 1.5rem;
        border-radius: 18px;
        margin: 1rem 0;
        max-width: 70%;
        margin-right: auto;
        border: 1px solid #E5E7EB;
    }

    /* Input area styling */
    .stTextArea textarea {
        background-color: #FFFFFF !important;
        border: 2px solid #E5E7EB !important;
        border-radius: 12px !important;
        color: #1F2937 !important;
        font-size: 16px !important;
        padding: 1rem !important;
        resize: none !important;
    }

    .stTextArea textarea:focus {
        border-color: #8b5cf6 !important;
        box-shadow: 0 0 0 3px rgba(139, 92, 246, 0.1) !important;
    }

    /* Button styling */
    .stButton > button {
        background: linear-gradient(135deg, #8b5cf6 0%, #ec4899 100%);
        color: white;
        border: none;
        padding: 0.75rem 2rem;
        border-radius: 8px;
        font-weight: 600;
        transition: all 0.3s;
        width: 100%;
    }

    .stButton > button:hover {
        box-shadow: 0 4px 20px rgba(139, 92, 246, 0.3);
        transform: translateY(-1px);
    }

    /* Headers */
    h1, h2, h3 {
        background: linear-gradient(135deg, #8b5cf6 0%, #ec4899 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        background-clip: text;
        font-weight: 700;
    }

    /* Gradient text */
    .gradient-text {
        background: linear-gradient(135deg, #8b5cf6 0%, #ec4899 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        background-clip: text;
        font-weight: 700;
    }

    /* Welcome screen */
    .welcome-container {
        text-align: center;
        padding: 4rem 2rem;
    }

    .logo-container {
        width: 120px;
        height: 120px;
        margin: 0 auto 2rem;
        background: linear-gradient(135deg, #8b5cf6 0%, #ec4899 100%);
        border-radius: 50%;
        display: flex;
        align-items: center;
        justify-content: center;
        font-size: 3rem;
        font-weight: 700;
        color: white;
        box-shadow: 0 8px 32px rgba(139, 92, 246, 0.25);
    }

    /* Project cards */
    .project-card {
        background: #FFFFFF;
        border: 1px solid #E5E7EB;
        border-radius: 12px;
        padding: 1rem;
        margin: 0.5rem 0;
        cursor: pointer;
        transition: all 0.3s;
    }

    .project-card:hover {
        border-color: #8b5cf6;
        transform: translateX(4px);
        box-shadow: 0 4px 12px rgba(139, 92, 246, 0.15);
    }

    /* Icon styles */
    .icon {
        width: 20px;
        height: 20px;
        margin-right: 0.75rem;
        stroke: #6B7280;
        stroke-width: 2;
        fill: none;
    }

    .project-card:hover .icon {
        stroke: #8b5cf6;
    }

    /* Sidebar sections */
    .sidebar-section {
        margin-bottom: 2rem;
    }

    .sidebar-header {
        font-size: 0.75rem;
        font-weight: 600;
        background: linear-gradient(135deg, #8b5cf6 0%, #ec4899 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        background-clip: text;
        text-transform: uppercase;
        letter-spacing: 0.1em;
        margin-bottom: 0.75rem;
    }

    /* Remove Streamlit's default padding */
    .block-container {
        padding: 0 !important;
    }

    /* Custom scrollbar */
    ::-webkit-scrollbar {
        width: 8px;
    }

    ::-webkit-scrollbar-track {
        background: #F9FAFB;
    }

    ::-webkit-scrollbar-thumb {
        background: #E5E7EB;
        border-radius: 4px;
    }

    ::-webkit-scrollbar-thumb:hover {
        background: #D1D5DB;
    }

    /* Status indicator */
    .status-indicator {
        display: inline-flex;
        align-items: center;
        gap: 0.5rem;
        padding: 0.25rem 0.75rem;
        background: rgba(139, 92, 246, 0.05);
        border: 1px solid rgba(139, 92, 246, 0.2);
        border-radius: 20px;
        font-size: 0.875rem;
        color: #8b5cf6;
    }

    .status-dot {
        width: 8px;
        height: 8px;
        background: #10b981;
        border-radius: 50%;
        animation: pulse 2s infinite;
    }

    @keyframes pulse {
        0% { opacity: 1; }
        50% { opacity: 0.5; }
        100% { opacity: 1; }
    }

    /* New button style */
    .new-button {
        display: flex;
        align-items: center;
        justify-content: center;
        padding: 0.5rem 1rem;
        border: 2px dashed #E5E7EB;
        border-radius: 8px;
        color: #6B7280;
        font-weight: 500;
        transition: all 0.3s;
        cursor: pointer;
        background: transparent;
        width: 100%;
        margin-top: 0.5rem;
    }

    .new-button:hover {
        border-color: #8b5cf6;
        color: #8b5cf6;
        background: rgba(139, 92, 246, 0.05);
    }

    /* Feature cards */
    .feature-card {
        background: white;
        border: 1px solid #E5E7EB;
        border-radius: 16px;
        padding: 2rem;
        text-align: center;
        transition: all 0.3s;
    }

    .feature-card:hover {
        border-color: #8b5cf6;
        box-shadow: 0 8px 24px rgba(139, 92, 246, 0.1);
        transform: translateY(-2px);
    }

    .feature-icon {
        width: 48px;
        height: 48px;
        margin: 0 auto 1rem;
        stroke: url(#gradient);
        stroke-width: 2;
        fill: none;
    }

    .feature-title {
        background: linear-gradient(135deg, #8b5cf6 0%, #ec4899 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        background-clip: text;
        font-weight: 600;
        font-size: 1.125rem;
        margin: 0.5rem 0;
    }

    .feature-desc {
        color: #6B7280;
        font-size: 0.875rem;
        line-height: 1.5;
    }
</style>

<!-- SVG definitions for gradients -->
<svg width="0" height="0">
    <defs>
        <linearGradient id="gradient" x1="0%" y1="0%" x2="100%" y2="100%">
            <stop offset="0%" style="stop-color:#8b5cf6;stop-opacity:1" />
            <stop offset="100%" style="stop-color:#ec4899;stop-opacity:1" />
        </linearGradient>
    </defs>
</svg>
""",
    unsafe_allow_html=True,
)

# Initialize session state
if "messages" not in st.session_state:
    st.session_state.messages = []

if "input_key" not in st.session_state:
    st.session_state.input_key = 0

# Sidebar
with st.sidebar:
    st.markdown('<div class="sidebar-section">', unsafe_allow_html=True)
    st.markdown('<div class="sidebar-header">Domain</div>', unsafe_allow_html=True)
    domain = st.selectbox(
        "Select domain",
        ["Quantitative Trading", "Software Development"],
        label_visibility="collapsed",
    )
    st.markdown("</div>", unsafe_allow_html=True)

    st.markdown('<div class="sidebar-section">', unsafe_allow_html=True)
    st.markdown('<div class="sidebar-header">Projects</div>', unsafe_allow_html=True)

    # Project buttons
    projects = [
        ("chart", "Strategy Backtest Q1"),
        ("trending", "Portfolio Optimization"),
        ("flask", "Alpha Research"),
        ("target", "Risk Analysis"),
    ]

    for icon, name in projects:
        st.markdown(
            f"""
        <div class="project-card">
            <svg class="icon" viewBox="0 0 24 24">
                {get_icon(icon)}
            </svg>
            <span style="color: #374151; font-weight: 500;">{name}</span>
        </div>
        """,
            unsafe_allow_html=True,
        )

    st.markdown(
        """
    <button class="new-button">
        <svg style="width: 20px; height: 20px; margin-right: 0.5rem;" viewBox="0 0 24 24" fill="none" stroke="currentColor">
            <line x1="12" y1="5" x2="12" y2="19"></line>
            <line x1="5" y1="12" x2="19" y2="12"></line>
        </svg>
        New Project
    </button>
    """,
        unsafe_allow_html=True,
    )

    st.markdown("</div>", unsafe_allow_html=True)

    st.divider()

    st.markdown('<div class="sidebar-section">', unsafe_allow_html=True)
    st.markdown(
        '<div class="sidebar-header">Recent Chats</div>', unsafe_allow_html=True
    )

    recent_chats = [
        "Mean reversion strategy help",
        "Debug portfolio allocation",
        "Optimize Sharpe ratio",
    ]

    for chat in recent_chats:
        if st.button(chat, key=f"chat_{chat}", use_container_width=True):
            pass

    st.markdown("</div>", unsafe_allow_html=True)

# Main content area
col1, col2, col3 = st.columns([1, 2, 1])

with col2:
    # Header
    st.markdown(
        """
    <div style="text-align: center; padding: 1rem 0; border-bottom: 1px solid #E5E7EB;">
        <h1 class="gradient-text" style="font-size: 2rem; margin: 0;">Luca</h1>
        <p style="color: #6B7280; font-size: 0.875rem; margin: 0.25rem 0 0 0;">Quantitative Development Assistant</p>
        <div class="status-indicator" style="margin-top: 0.5rem;">
            <div class="status-dot"></div>
            <span>Ready</span>
        </div>
    </div>
    """,
        unsafe_allow_html=True,
    )

    # Chat container
    chat_container = st.container()

    with chat_container:
        if len(st.session_state.messages) == 0:
            # Welcome screen
            st.markdown(
                """
            <div class="welcome-container">
                <div class="logo-container">L</div>
                <h2 class="gradient-text" style="font-size: 3rem; margin-bottom: 1rem;">Welcome to Luca</h2>
                <p style="color: #6B7280; font-size: 1.125rem; margin-bottom: 3rem;">
                    Your AI-powered quantitative development assistant
                </p>
                <div style="display: grid; grid-template-columns: repeat(3, 1fr); gap: 1rem; max-width: 600px; margin: 0 auto;">
                    <div class="feature-card">
                        <svg class="feature-icon" viewBox="0 0 24 24">
                            <polyline points="22 12 18 12 15 21 9 3 6 12 2 12"></polyline>
                        </svg>
                        <h4 class="feature-title">Strategy Development</h4>
                        <p class="feature-desc">Build and test trading strategies with AI assistance</p>
                    </div>
                    <div class="feature-card">
                        <svg class="feature-icon" viewBox="0 0 24 24">
                            <path d="M13 2L3 14h9l-1 8 10-12h-9l1-8z"></path>
                        </svg>
                        <h4 class="feature-title">Backtesting</h4>
                        <p class="feature-desc">Run comprehensive backtests with real market data</p>
                    </div>
                    <div class="feature-card">
                        <svg class="feature-icon" viewBox="0 0 24 24">
                            <circle cx="12" cy="12" r="3"></circle>
                            <path d="M12 1v6m0 6v6m-9-9h6m6 0h6"></path>
                        </svg>
                        <h4 class="feature-title">Optimization</h4>
                        <p class="feature-desc">Optimize strategies for maximum performance</p>
                    </div>
                </div>
            </div>
            """,
                unsafe_allow_html=True,
            )
        else:
            # Display messages
            for message in st.session_state.messages:
                if message["role"] == "user":
                    st.markdown(
                        f'<div class="user-message">{message["content"]}</div>',
                        unsafe_allow_html=True,
                    )
                else:
                    st.markdown(
                        f'<div class="assistant-message">{message["content"]}</div>',
                        unsafe_allow_html=True,
                    )

    # Input area
    st.markdown('<div style="height: 2rem;"></div>', unsafe_allow_html=True)

    with st.form(key=f"chat_form_{st.session_state.input_key}", clear_on_submit=True):
        user_input = st.text_area(
            "Message Luca...",
            height=80,
            placeholder="Type your message here...",
            label_visibility="collapsed",
            key=f"input_{st.session_state.input_key}",
        )

        col1, col2, col3 = st.columns([2, 1, 2])
        with col2:
            submitted = st.form_submit_button("Send", use_container_width=True)

        if submitted and user_input:
            # Add user message
            st.session_state.messages.append({"role": "user", "content": user_input})

            # Simulate assistant response
            with st.spinner(""):
                time.sleep(1)
                response = f"I understand you're interested in '{user_input}'. Let me help you build a strategy for that!"
                st.session_state.messages.append(
                    {"role": "assistant", "content": response}
                )

            # Increment key to reset form
            st.session_state.input_key += 1
            st.rerun()
