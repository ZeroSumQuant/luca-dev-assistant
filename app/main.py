"""Streamlit UI for LUCA Dev Assistant."""

import asyncio
import logging
import sys
from pathlib import Path

import streamlit as st
from dotenv import load_dotenv

# Add parent directory to sys.path for importing from project root
sys.path.insert(0, str(Path(__file__).parent.parent))

# Import theme
from app.theme import get_theme_css, render_icon

# Import Luca components
from luca import get_manager
from luca_core.manager.manager import ResponseOptions
from luca_core.schemas import LearningMode

# Load environment variables
load_dotenv()

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
)
logger = logging.getLogger(__name__)

# Configure the page
st.set_page_config(
    page_title="Luca - Quantitative Development Assistant",
    page_icon="L",
    layout="wide",
    initial_sidebar_state="expanded",
)

# Apply the modern theme
st.markdown(get_theme_css(), unsafe_allow_html=True)

# Additional page-specific styles
st.markdown(
    """
<style>
    /* Chat-specific additions */
    .stChatMessage {
        background-color: transparent;
        border: none;
        padding: 1rem 0;
    }

    .stChatMessage[data-testid="user-message"] {
        background: linear-gradient(135deg, #8b5cf6 0%, #ec4899 100%);
        color: white;
        border-radius: 18px;
        padding: 1rem 1.5rem;
        margin: 0.5rem 0;
        max-width: 70%;
        margin-left: auto;
    }

    .stChatMessage[data-testid="assistant-message"] {
        background: #F3F4F6;
        color: #1F2937;
        border-radius: 18px;
        padding: 1rem 1.5rem;
        margin: 0.5rem 0;
        max-width: 70%;
        margin-right: auto;
    }

    /* Welcome screen */
    .welcome-title {
        font-size: 3rem;
        font-weight: 700;
        margin-bottom: 0.5rem;
        background: linear-gradient(135deg, #8b5cf6 0%, #ec4899 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        background-clip: text;
    }

    /* Chat input enhancement */
    .stChatInput textarea {
        background-color: #FFFFFF !important;
        border: 2px solid #E5E7EB !important;
        border-radius: 12px !important;
        font-size: 16px !important;
    }

    .stChatInput textarea:focus {
        border-color: #8b5cf6 !important;
        box-shadow: 0 0 0 3px rgba(139, 92, 246, 0.1) !important;
    }

    /* Typing indicator */
    .typing-dot {
        width: 8px;
        height: 8px;
        background: #8b5cf6;
        border-radius: 50%;
        display: inline-block;
        margin: 0 2px;
    }
</style>
""",
    unsafe_allow_html=True,
)


# Initialize Luca manager in session state
async def init_manager():
    """Initialize the Luca manager and store in session state."""
    manager = get_manager()
    await manager.initialize()
    return manager


def get_learning_mode():
    """Get the current learning mode from session state."""
    if "learning_mode" not in st.session_state:
        st.session_state.learning_mode = LearningMode.PRO
    return st.session_state.learning_mode


def set_learning_mode(mode_str):
    """Set the learning mode in session state."""
    st.session_state.learning_mode = LearningMode(mode_str)


def main():
    # Sidebar with navigation and projects
    with st.sidebar:
        # Logo section
        st.markdown(
            """
        <div style="text-align: center; padding: 1rem 0; margin-bottom: 1rem;">
            <h2 class="gradient-text" style="margin: 0;">Luca</h2>
            <p style="color: #6B7280; font-size: 0.875rem; margin: 0;">Quantitative Assistant</p>
        </div>
        """,
            unsafe_allow_html=True,
        )

        # Domain selector
        st.markdown('<div class="sidebar-section">', unsafe_allow_html=True)
        st.markdown('<div class="sidebar-header">Domain</div>', unsafe_allow_html=True)
        domain = st.selectbox(
            "Domain",
            ["Quantitative Trading", "Software Development"],
            label_visibility="collapsed",
        )
        st.markdown("</div>", unsafe_allow_html=True)

        # Projects section
        st.markdown('<div class="sidebar-section">', unsafe_allow_html=True)
        st.markdown(
            '<div class="sidebar-header">Projects</div>', unsafe_allow_html=True
        )

        # Example project cards
        if "selected_project" not in st.session_state:
            st.session_state.selected_project = None

        projects = [
            {"icon": "chart", "name": "Strategy Backtest Q1", "id": "proj_1"},
            {"icon": "trending", "name": "Portfolio Optimization", "id": "proj_2"},
            {"icon": "flask", "name": "Alpha Research", "id": "proj_3"},
            {"icon": "target", "name": "Risk Analysis", "id": "proj_4"},
        ]

        for project in projects:
            col1, col2 = st.columns([0.15, 0.85])
            with col1:
                st.markdown(
                    render_icon(project["icon"], size=20), unsafe_allow_html=True
                )
            with col2:
                if st.button(
                    project["name"],
                    key=project["id"],
                    use_container_width=True,
                    help=f"Open {project['name']}",
                ):
                    st.session_state.selected_project = project["id"]
                    st.rerun()

        # New project button
        st.markdown(
            """
        <button class="new-button" style="width: 100%; margin-top: 0.5rem;">
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

        # Recent chats section
        st.markdown(
            '<div class="sidebar-header">RECENT CHATS</div>', unsafe_allow_html=True
        )

        # Example recent chats
        recent_chats = [
            "Mean reversion strategy help",
            "Debug portfolio allocation",
            "Optimize Sharpe ratio",
        ]

        for chat in recent_chats:
            st.button(chat, key=f"chat_{chat}", use_container_width=True)

        st.divider()

        # Settings at bottom
        with st.expander("Settings"):
            current_mode = get_learning_mode()
            mode = st.selectbox(
                "Response Style",
                options=[LearningMode.NOOB, LearningMode.PRO, LearningMode.GURU],
                format_func=lambda x: x.title(),
                index=[LearningMode.NOOB, LearningMode.PRO, LearningMode.GURU].index(
                    current_mode
                ),
            )
            if mode != current_mode:
                set_learning_mode(mode)
                st.rerun()

    # Initialize chat history first
    if "messages" not in st.session_state:
        st.session_state.messages = [
            {
                "role": "assistant",
                "content": (
                    "Hello! I'm Luca, your quantitative development assistant. "
                    "I can help you build trading strategies, run backtests, "
                    "optimize parameters, and analyze results. What would you like to work on today?"
                ),
            }
        ]

    # Main chat area - clean, minimal header
    if len(st.session_state.messages) == 1:
        # Show welcome screen when no conversation
        st.markdown(
            """
            <div style="text-align: center; padding: 3rem 0;">
                <h1 class="welcome-title">Luca</h1>
                <p style="font-size: 1.2rem; color: #6B7280;">Your Quantitative Development Assistant</p>
            </div>
            """,
            unsafe_allow_html=True,
        )

    # Create a container for messages to control styling
    messages_container = st.container()

    # Display chat history
    with messages_container:
        for message in st.session_state.messages:
            with st.chat_message(
                message["role"],
                avatar=None,  # We'll use custom styling instead of emojis
            ):
                st.markdown(message["content"])

    # Chat input at the bottom
    if prompt := st.chat_input("Message Luca..."):
        # Add user message to chat history
        st.session_state.messages.append({"role": "user", "content": prompt})

        # Display user message
        with messages_container:
            with st.chat_message("user", avatar=None):
                st.markdown(prompt)

        # Process the request using the LucaManager
        with messages_container:
            with st.chat_message("assistant", avatar=None):
                message_placeholder = st.empty()
                # Show typing indicator
                typing_indicator = message_placeholder.container()
                typing_cols = typing_indicator.columns([0.1, 10])
                with typing_cols[0]:
                    st.markdown(
                        """<div style="display: flex; gap: 4px;">
                        <div class="typing-dot" style="animation: bounce 1.4s infinite;"></div>
                        <div class="typing-dot" style="animation: bounce 1.4s infinite 0.2s;"></div>
                        <div class="typing-dot" style="animation: bounce 1.4s infinite 0.4s;"></div>
                        </div>
                        <style>
                        @keyframes bounce {
                            0%, 60%, 100% { transform: translateY(0); }
                            30% { transform: translateY(-10px); }
                        }
                        </style>""",
                        unsafe_allow_html=True,
                    )

                try:
                    # Create response options based on learning mode
                    response_options = ResponseOptions(
                        learning_mode=get_learning_mode(),
                        verbose=False,
                        include_agent_info=True,
                    )

                    # Execute async manager in event loop
                    async def process():
                        manager = get_manager()
                        await manager.initialize()  # Ensure manager is initialized
                        return await manager.process_request(prompt, response_options)

                    full_response = asyncio.run(process())

                    # Clear typing indicator and show response
                    typing_indicator.empty()
                    message_placeholder.markdown(full_response)

                    # Add assistant response to chat history
                    st.session_state.messages.append(
                        {"role": "assistant", "content": full_response}
                    )
                except Exception as e:
                    logger.error(f"Error processing request: {e}")
                    error_msg = (
                        f"I encountered an error while processing your request:\n\n"
                        f"```\n{str(e)}\n```\n\n"
                        f"Please try again with a simpler request or check the logs for more details."
                    )
                    typing_indicator.empty()
                    message_placeholder.markdown(error_msg)
                    st.session_state.messages.append(
                        {"role": "assistant", "content": error_msg}
                    )

    # No footer - keep it clean like Claude/ChatGPT


if __name__ == "__main__":
    main()
