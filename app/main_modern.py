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
        background: radial-gradient(circle at 30% 30%, #ec4899 0%, #8b5cf6 50%, #6d28d9 100%);
        border-radius: 50%;
        display: flex;
        align-items: center;
        justify-content: center;
        position: relative;
        cursor: pointer;
        transition: all 0.4s ease;
        animation: pulse-glow 3.6s ease-in-out infinite, rotate-hue 10s linear infinite;
        overflow: hidden;
    }

    .logo-container::before {
        content: '';
        position: absolute;
        top: -20px;
        left: -20px;
        right: -20px;
        bottom: -20px;
        background: radial-gradient(circle, rgba(139, 92, 246, 0.4) 0%, rgba(236, 72, 153, 0.3) 50%, transparent 70%);
        border-radius: 50%;
        z-index: -1;
        opacity: 0.6;
        animation: aura-pulse 3.6s ease-in-out infinite;
    }

    .logo-container::after {
        content: '';
        position: absolute;
        top: -40px;
        left: -40px;
        right: -40px;
        bottom: -40px;
        background: radial-gradient(circle, rgba(139, 92, 246, 0.2) 0%, rgba(236, 72, 153, 0.1) 40%, transparent 60%);
        border-radius: 50%;
        z-index: -2;
        opacity: 0.4;
        animation: aura-pulse 3.6s ease-in-out infinite 0.5s;
    }

    .logo-container:hover {
        transform: scale(1.1);
        box-shadow: 0 0 60px rgba(139, 92, 246, 0.6), 0 0 100px rgba(236, 72, 153, 0.4);
        filter: brightness(1.3);
    }

    .logo-container:active {
        transform: scale(0.95);
        box-shadow: 0 0 30px rgba(139, 92, 246, 0.4), 0 0 50px rgba(236, 72, 153, 0.3);
        filter: brightness(0.9);
        transition: all 0.1s ease;
    }

    .logo-container:hover::before {
        opacity: 1;
        animation-duration: 1.5s;
    }

    .logo-container:hover::after {
        opacity: 0.7;
        animation-duration: 1.5s;
    }

    @keyframes pulse-glow {
        0%, 100% {
            box-shadow: 0 0 30px rgba(139, 92, 246, 0.5), 0 0 60px rgba(236, 72, 153, 0.3);
        }
        50% {
            box-shadow: 0 0 40px rgba(139, 92, 246, 0.6), 0 0 80px rgba(236, 72, 153, 0.4);
        }
    }

    @keyframes aura-pulse {
        0%, 100% {
            transform: scale(1);
            opacity: 0.6;
        }
        50% {
            transform: scale(1.1);
            opacity: 0.3;
        }
    }

    .orb-inner {
        position: absolute;
        width: 100%;
        height: 100%;
        border-radius: 50%;
        background: conic-gradient(from 0deg at 50% 50%,
            transparent 0deg,
            rgba(236, 72, 153, 0.4) 60deg,
            transparent 120deg,
            rgba(139, 92, 246, 0.4) 180deg,
            transparent 240deg,
            rgba(236, 72, 153, 0.4) 300deg,
            transparent 360deg);
        animation: swirl 5s linear infinite;
    }

    .orb-inner::before {
        content: '';
        position: absolute;
        inset: 20%;
        border-radius: 50%;
        background: radial-gradient(circle,
            rgba(255, 255, 255, 0.3) 0%,
            transparent 70%);
        animation: shimmer 3.6s ease-in-out infinite;
    }

    .orb-particles {
        position: absolute;
        width: 100%;
        height: 100%;
        border-radius: 50%;
    }

    .orb-particles::before,
    .orb-particles::after {
        content: '';
        position: absolute;
        width: 4px;
        height: 4px;
        background: white;
        border-radius: 50%;
        box-shadow: 0 0 10px rgba(255, 255, 255, 0.8);
        animation: orbit 7.2s linear infinite;
    }

    .orb-particles::after {
        animation-delay: -3s;
        width: 3px;
        height: 3px;
    }

    @keyframes swirl {
        0% {
            transform: rotate(0deg);
        }
        100% {
            transform: rotate(360deg);
        }
    }

    @keyframes shimmer {
        0%, 100% {
            opacity: 0.5;
            transform: scale(0.8);
        }
        50% {
            opacity: 1;
            transform: scale(1.1);
        }
    }

    @keyframes orbit {
        0% {
            transform: rotate(0deg) translateX(40px) rotate(0deg);
            opacity: 0;
        }
        10% {
            opacity: 1;
        }
        90% {
            opacity: 1;
        }
        100% {
            transform: rotate(360deg) translateX(40px) rotate(-360deg);
            opacity: 0;
        }
    }

    @keyframes rotate-hue {
        0% {
            filter: hue-rotate(0deg) brightness(1);
        }
        50% {
            filter: hue-rotate(20deg) brightness(1.1);
        }
        100% {
            filter: hue-rotate(0deg) brightness(1);
        }
    }

    /* Excited State - back to original speed */
    .logo-container.excited {
        animation: pulse-glow 3s ease-in-out infinite, rotate-hue 8s linear infinite, excitement-bounce 0.5s ease-in-out infinite;
        filter: brightness(1.8) saturate(1.5) hue-rotate(0deg);
        transform: scale(1.15);
        box-shadow: 0 0 100px rgba(139, 92, 246, 1), 0 0 200px rgba(236, 72, 153, 0.8);
    }

    .logo-container.excited .orb-particles::before,
    .logo-container.excited .orb-particles::after {
        animation: orbit 6s linear infinite;
    }

    .logo-container.excited .orb-inner {
        animation: swirl 4s linear infinite;
    }

    .logo-container.excited::before,
    .logo-container.excited::after {
        animation: aura-pulse 3s ease-in-out infinite;
        opacity: 1 !important;
    }

    @keyframes excitement-bounce {
        0%, 100% {
            transform: scale(1.2) translateY(0);
        }
        50% {
            transform: scale(1.25) translateY(-5px);
        }
    }

    /* Extra spinning orbs for excited state */
    .extra-orbs {
        position: absolute;
        top: 50%;
        left: 50%;
        transform: translate(-50%, -50%);
        width: 120px;
        height: 120px;
        pointer-events: none;
        opacity: 0;
        transition: opacity 0.3s ease;
    }

    .logo-container.excited + .extra-orbs {
        opacity: 1;
    }

    .extra-orb {
        position: absolute;
        width: 20px;
        height: 20px;
        background: radial-gradient(circle, #ffffff 0%, #ffffff 30%, rgba(255, 255, 255, 0.6) 60%, transparent 100%);
        border-radius: 50%;
        box-shadow: 0 0 20px rgba(255, 255, 255, 1), 0 0 40px rgba(255, 255, 255, 0.8);
        top: 50%;
        left: 50%;
        transform: translate(-50%, -50%);
    }

    .extra-orb:nth-child(1) {
        animation: spin-orbit-1 1.5s linear infinite;
    }

    .extra-orb:nth-child(2) {
        animation: spin-orbit-2 1.8s linear infinite;
    }

    .extra-orb:nth-child(3) {
        animation: spin-orbit-3 1.2s linear infinite;
    }

    .extra-orb:nth-child(4) {
        animation: spin-orbit-4 2s linear infinite;
    }

    .extra-orb:nth-child(5) {
        animation: spin-orbit-5 1s linear infinite;
    }

    @keyframes spin-orbit-1 {
        0% {
            transform: rotate(0deg) translateX(80px) rotate(0deg) scale(0.8);
        }
        50% {
            transform: rotate(180deg) translateX(80px) rotate(-180deg) scale(1.2);
        }
        100% {
            transform: rotate(360deg) translateX(80px) rotate(-360deg) scale(0.8);
        }
    }

    @keyframes spin-orbit-2 {
        0% {
            transform: rotate(72deg) translateX(90px) rotate(-72deg) scale(1);
        }
        100% {
            transform: rotate(432deg) translateX(90px) rotate(-432deg) scale(1);
        }
    }

    @keyframes spin-orbit-3 {
        0% {
            transform: rotate(144deg) translateX(70px) rotate(-144deg) scale(1.1);
        }
        100% {
            transform: rotate(504deg) translateX(70px) rotate(-504deg) scale(1.1);
        }
    }

    @keyframes spin-orbit-4 {
        0% {
            transform: rotate(216deg) translateX(85px) rotate(-216deg) scale(0.9);
        }
        100% {
            transform: rotate(576deg) translateX(85px) rotate(-576deg) scale(0.9);
        }
    }

    @keyframes spin-orbit-5 {
        0% {
            transform: rotate(288deg) translateX(75px) rotate(-288deg) scale(1.3);
        }
        50% {
            transform: rotate(468deg) translateX(75px) rotate(-468deg) scale(0.7);
        }
        100% {
            transform: rotate(648deg) translateX(75px) rotate(-648deg) scale(1.3);
        }
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

    /* Model Selector Dropdown */
    .model-dropdown-container {
        position: relative;
        display: inline-block;
        margin: 0 auto;
    }

    .model-dropdown {
        position: absolute;
        top: 50%;
        left: 130px;
        transform: translateY(-50%) scale(0.95);
        background: white;
        border-radius: 16px;
        padding: 0.5rem;
        min-width: 280px;
        box-shadow: 0 10px 40px rgba(0, 0, 0, 0.1), 0 0 0 1px rgba(229, 231, 235, 0.5);
        opacity: 0;
        pointer-events: none;
        transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
        z-index: 1000;
    }

    .model-dropdown.active {
        opacity: 1;
        pointer-events: all;
        transform: translateY(-50%) scale(1);
    }

    .model-dropdown::before {
        content: '';
        position: absolute;
        top: 50%;
        left: -8px;
        transform: translateY(-50%) rotate(45deg);
        width: 16px;
        height: 16px;
        background: white;
        border-left: 1px solid rgba(229, 231, 235, 0.5);
        border-bottom: 1px solid rgba(229, 231, 235, 0.5);
    }

    .model-option {
        background: white;
        border: 2px solid transparent;
        border-radius: 12px;
        padding: 0.75rem 1rem;
        margin: 0.25rem 0;
        cursor: pointer;
        transition: all 0.2s ease;
        display: flex;
        align-items: center;
        justify-content: space-between;
    }

    .model-option:hover {
        background: rgba(139, 92, 246, 0.05);
        border-color: rgba(139, 92, 246, 0.3);
        transform: translateX(4px);
    }

    .model-option.selected {
        background: linear-gradient(135deg, rgba(139, 92, 246, 0.1) 0%, rgba(236, 72, 153, 0.05) 100%);
        border-color: #8b5cf6;
    }

    .model-info {
        flex: 1;
    }

    .model-name {
        font-weight: 600;
        color: #1F2937;
        font-size: 0.95rem;
        margin-bottom: 0.15rem;
    }

    .model-desc {
        font-size: 0.75rem;
        color: #6B7280;
    }

    .model-indicator {
        width: 8px;
        height: 8px;
        border-radius: 50%;
        background: linear-gradient(135deg, #8b5cf6 0%, #ec4899 100%);
        opacity: 0;
        transition: opacity 0.2s ease;
    }

    .model-option.selected .model-indicator {
        opacity: 1;
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

if "selected_model" not in st.session_state:
    st.session_state.selected_model = "GPT-4o"

if "show_model_selector" not in st.session_state:
    st.session_state.show_model_selector = False

# Sidebar
with st.sidebar:
    # Navigation link
    st.page_link("pages/agent_manager.py", label="Agent Manager", use_container_width=True)
    
    st.divider()
    
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
        st.markdown(
            f"""
        <div class="project-card">
            <svg class="icon" viewBox="0 0 24 24">
                <path d="M21 15a2 2 0 0 1-2 2H7l-4 4V5a2 2 0 0 1 2-2h14a2 2 0 0 1 2 2z"></path>
            </svg>
            <span style="color: #374151; font-weight: 500;">{chat}</span>
        </div>
        """,
            unsafe_allow_html=True,
        )

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
                f"""
            <div class="welcome-container">
                <div class="model-dropdown-container">
                    <div class="logo-container" title="Click to change model">
                        <div class="orb-inner"></div>
                        <div class="orb-particles"></div>
                    </div>
                    <div class="extra-orbs">
                        <div class="extra-orb"></div>
                        <div class="extra-orb"></div>
                        <div class="extra-orb"></div>
                        <div class="extra-orb"></div>
                        <div class="extra-orb"></div>
                    </div>
                    <div id="model-dropdown" class="model-dropdown">
                        <div class="model-option selected">
                            <div class="model-info">
                                <div class="model-name">GPT-4o</div>
                                <div class="model-desc">Most capable, best for complex tasks</div>
                            </div>
                            <div class="model-indicator"></div>
                        </div>
                        <div class="model-option">
                            <div class="model-info">
                                <div class="model-name">GPT-4 Turbo</div>
                                <div class="model-desc">Fast and capable</div>
                            </div>
                            <div class="model-indicator"></div>
                        </div>
                        <div class="model-option">
                            <div class="model-info">
                                <div class="model-name">Claude 3 Opus</div>
                                <div class="model-desc">Advanced reasoning</div>
                            </div>
                            <div class="model-indicator"></div>
                        </div>
                        <div class="model-option">
                            <div class="model-info">
                                <div class="model-name">Claude 3 Sonnet</div>
                                <div class="model-desc">Balanced performance</div>
                            </div>
                            <div class="model-indicator"></div>
                        </div>
                    </div>
                </div>
                <h2 class="gradient-text" style="font-size: 3rem; margin-bottom: 1rem;">Welcome to Luca</h2>
                <p style="color: #6B7280; font-size: 1.125rem; margin-bottom: 2rem;">
                    Your AI-powered quantitative development assistant
                </p>
                <p style="color: #8b5cf6; font-size: 0.875rem; margin-bottom: 1rem;">
                    Currently using: <strong class="model-display">{st.session_state.selected_model}</strong>
                </p>
                <button data-test-excitement="true" style="background: #8b5cf6; color: white; border: none; padding: 0.5rem 1rem; border-radius: 8px; margin-bottom: 2rem; cursor: pointer;">Test Excitement</button>
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

    # Use components.html for better JavaScript execution
    import streamlit.components.v1 as components

    # Inject the JavaScript properly
    components.html(
        """
        <script>
        (function() {
            // Wait for parent document to be ready
            function initializeLuca() {
                const parentDoc = window.parent.document;

                // Initialize click tracking
                if (!window.parent.lucaClickCount) {
                    window.parent.lucaClickCount = 0;
                    window.parent.lucaClickTimer = null;
                    window.parent.lucaExcitementTimer = null;
                }

                // Handle orb clicks
                function handleOrbClick() {
                    const orb = parentDoc.querySelector('.logo-container');
                    const dropdown = parentDoc.getElementById('model-dropdown');
                    const extraOrbs = parentDoc.querySelector('.extra-orbs');

                    if (!orb || !dropdown) {
                        console.log('Elements not found');
                        return;
                    }

                    // Increment click count
                    window.parent.lucaClickCount++;

                    // Reset click count timer
                    clearTimeout(window.parent.lucaClickTimer);
                    window.parent.lucaClickTimer = setTimeout(() => {
                        window.parent.lucaClickCount = 0;
                    }, 1000);

                    // Check for excitement state
                    if (window.parent.lucaClickCount >= 3) {
                        orb.classList.add('excited');
                        if (extraOrbs) extraOrbs.style.opacity = '1';
                        console.log('EXCITED STATE ACTIVATED!');

                        // Clear any existing calm down timer
                        clearTimeout(window.parent.lucaExcitementTimer);

                        // Set calm down timer
                        window.parent.lucaExcitementTimer = setTimeout(() => {
                            orb.classList.remove('excited');
                            if (extraOrbs) extraOrbs.style.opacity = '0';
                            window.parent.lucaClickCount = 0;
                            console.log('Calming down...');
                        }, 5000);
                    } else {
                        console.log('Orb clicked', window.parent.lucaClickCount, 'times');
                    }

                    // Toggle dropdown
                    dropdown.classList.toggle('active');
                }

                // Select model function
                function selectModel(modelName) {
                    const options = parentDoc.querySelectorAll('.model-option');
                    options.forEach(el => el.classList.remove('selected'));

                    // Find and select the clicked option
                    options.forEach(el => {
                        if (el.querySelector('.model-name').textContent === modelName) {
                            el.classList.add('selected');
                        }
                    });

                    parentDoc.getElementById('model-dropdown').classList.remove('active');

                    const modelDisplay = parentDoc.querySelector('.model-display');
                    if (modelDisplay) {
                        modelDisplay.textContent = modelName;
                    }
                }

                // Attach event listeners
                function attachListeners() {
                    const orb = parentDoc.querySelector('.logo-container');
                    if (orb && !orb.hasAttribute('data-luca-listeners')) {
                        orb.setAttribute('data-luca-listeners', 'true');
                        orb.addEventListener('click', handleOrbClick);
                        console.log('Orb listener attached');
                    }

                    // Attach model option listeners
                    const modelOptions = parentDoc.querySelectorAll('.model-option');
                    modelOptions.forEach(option => {
                        if (!option.hasAttribute('data-luca-listeners')) {
                            option.setAttribute('data-luca-listeners', 'true');
                            option.addEventListener('click', function(e) {
                                e.stopPropagation();
                                const modelName = this.querySelector('.model-name').textContent;
                                selectModel(modelName);
                            });
                        }
                    });

                    // Test button listener
                    const testBtn = parentDoc.querySelector('[data-test-excitement]');
                    if (testBtn && !testBtn.hasAttribute('data-luca-listeners')) {
                        testBtn.setAttribute('data-luca-listeners', 'true');
                        testBtn.addEventListener('click', function() {
                            const orb = parentDoc.querySelector('.logo-container');
                            const extraOrbs = parentDoc.querySelector('.extra-orbs');
                            if (orb) {
                                orb.classList.add('excited');
                                if (extraOrbs) extraOrbs.style.opacity = '1';
                                console.log('Test button: Excitement triggered');
                                setTimeout(() => {
                                    orb.classList.remove('excited');
                                    if (extraOrbs) extraOrbs.style.opacity = '0';
                                }, 5000);
                            }
                        });
                        console.log('Test button listener attached');
                    }
                }

                // Global click handler for closing dropdown
                if (!window.parent.lucaGlobalClickHandler) {
                    window.parent.lucaGlobalClickHandler = true;
                    parentDoc.addEventListener('click', function(event) {
                        const dropdown = parentDoc.getElementById('model-dropdown');
                        const orb = parentDoc.querySelector('.logo-container');
                        const extraOrbs = parentDoc.querySelector('.extra-orbs');

                        if (dropdown && orb && !dropdown.contains(event.target) &&
                            !orb.contains(event.target) &&
                            (!extraOrbs || !extraOrbs.contains(event.target))) {
                            dropdown.classList.remove('active');
                        }
                    });
                }

                // Attach listeners
                attachListeners();

                // Set up mutation observer
                if (!window.parent.lucaObserver) {
                    window.parent.lucaObserver = new MutationObserver(function() {
                        attachListeners();
                    });

                    window.parent.lucaObserver.observe(parentDoc.body, {
                        childList: true,
                        subtree: true
                    });
                }
            }

            // Initialize when ready
            if (document.readyState === 'complete') {
                initializeLuca();
            } else {
                window.addEventListener('load', initializeLuca);
            }

            // Also try immediately
            setTimeout(initializeLuca, 100);
            setTimeout(initializeLuca, 500);
            setTimeout(initializeLuca, 1000);
        })();
        </script>
        """,
        height=0,
    )
