"""Streamlit UI for LUCA Dev Assistant."""

import asyncio
import logging
import sys
from pathlib import Path

import streamlit as st
from dotenv import load_dotenv

# Add parent directory to sys.path for importing from project root
sys.path.insert(0, str(Path(__file__).parent.parent))

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
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded",
)

# Custom CSS for Claude/ChatGPT-style interface
CSS_STYLES = """
<style>
    /* Main container adjustments */
    .main .block-container {
        padding-top: 2rem;
        padding-bottom: 2rem;
        max-width: 1000px;
    }

    /* Hide default Streamlit elements */
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    header {visibility: hidden;}

    /* Chat messages styling */
    .stChatMessage {
        background-color: transparent;
        border: none;
        padding: 1rem 0;
    }

    .stChatMessage[data-testid="user-message"] {
        background-color: #f7f7f8;
        border-radius: 1rem;
        margin: 0.5rem 0;
    }

    /* Message content styling */
    .stMarkdown {
        font-size: 1rem;
        line-height: 1.6;
        color: #2c3e50;
    }

    /* Sidebar styling */
    section[data-testid="stSidebar"] {
        background-color: #f9f9f9;
        border-right: 1px solid #e5e5e5;
    }

    /* Sidebar content */
    section[data-testid="stSidebar"] > div {
        padding-top: 1rem;
    }

    /* Code blocks */
    .stMarkdown pre {
        background-color: #1e1e1e;
        color: #d4d4d4;
        border-radius: 0.5rem;
        padding: 1rem;
        position: relative;
        font-family: 'Monaco', 'Menlo', 'Ubuntu Mono', monospace;
        font-size: 0.875rem;
        line-height: 1.5;
    }

    /* Code syntax highlighting */
    .stMarkdown code {
        background-color: #f4f4f4;
        padding: 0.2rem 0.4rem;
        border-radius: 0.25rem;
        font-size: 0.875rem;
    }

    /* Headers */
    h1, h2, h3 {
        font-weight: 600;
        color: #1a1a1a;
    }

    /* Input area */
    .stChatInputContainer {
        border-top: 1px solid #e5e5e5;
        padding-top: 1rem;
        background-color: white;
    }

    /* Chat input styling */
    .stChatInput textarea {
        font-size: 1rem;
        border: 1px solid #e5e5e5;
        border-radius: 0.5rem;
    }

    .stChatInput textarea:focus {
        border-color: #1a73e8;
        box-shadow: 0 0 0 2px rgba(26,115,232,0.1);
    }

    /* Sidebar headers */
    .sidebar-header {
        font-size: 0.875rem;
        font-weight: 600;
        color: #666;
        text-transform: uppercase;
        letter-spacing: 0.05em;
        margin: 1rem 0 0.5rem 0;
    }

    /* Project cards */
    .project-card {
        background: white;
        border: 1px solid #e5e5e5;
        border-radius: 0.5rem;
        padding: 0.75rem;
        margin: 0.5rem 0;
        cursor: pointer;
        transition: all 0.2s;
    }

    .project-card:hover {
        border-color: #1a73e8;
        box-shadow: 0 1px 3px rgba(0,0,0,0.1);
    }

    /* Domain selector */
    .domain-selector {
        background: #f1f3f4;
        border-radius: 0.5rem;
        padding: 0.5rem;
        margin-bottom: 1rem;
    }
</style>
"""

st.markdown(CSS_STYLES, unsafe_allow_html=True)


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
        # Domain selector at top
        st.markdown('<div class="domain-selector">', unsafe_allow_html=True)
        domain = st.selectbox(
            "Domain",
            ["Quantitative Trading", "Software Development"],
            label_visibility="collapsed",
        )
        st.markdown("</div>", unsafe_allow_html=True)

        # Projects section
        st.markdown(
            '<div class="sidebar-header">PROJECTS</div>', unsafe_allow_html=True
        )

        # Example project cards
        if "selected_project" not in st.session_state:
            st.session_state.selected_project = None

        projects = [
            {"icon": "📊", "name": "Strategy Backtest Q1", "id": "proj_1"},
            {"icon": "📈", "name": "Portfolio Optimization", "id": "proj_2"},
            {"icon": "🔬", "name": "Alpha Research", "id": "proj_3"},
            {"icon": "🎯", "name": "Risk Analysis", "id": "proj_4"},
        ]

        for project in projects:
            if st.button(
                f"{project['icon']} {project['name']}",
                key=project["id"],
                use_container_width=True,
            ):
                st.session_state.selected_project = project["id"]
                st.rerun()

        # New project button
        if st.button("➕ New Project", use_container_width=True):
            st.session_state.selected_project = "new"
            st.rerun()

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
        with st.expander("⚙️ Settings"):
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

    # Main chat area - clean, minimal header
    if not st.session_state.messages or len(st.session_state.messages) == 1:
        # Show welcome screen when no conversation
        st.markdown(
            """
            <div style="text-align: center; padding: 3rem 0;">
                <h1 style="font-size: 3rem; font-weight: 600; margin-bottom: 0.5rem;">Luca</h1>
                <p style="font-size: 1.2rem; color: #666;">Your Quantitative Development Assistant</p>
            </div>
            """,
            unsafe_allow_html=True,
        )

    # Initialize chat history
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

    # Create a container for messages to control styling
    messages_container = st.container()

    # Display chat history
    with messages_container:
        for message in st.session_state.messages:
            with st.chat_message(
                message["role"],
                avatar="🤖" if message["role"] == "assistant" else "👤",
            ):
                st.markdown(message["content"])

    # Chat input at the bottom
    if prompt := st.chat_input("Message Luca..."):
        # Add user message to chat history
        st.session_state.messages.append({"role": "user", "content": prompt})

        # Display user message
        with messages_container:
            with st.chat_message("user", avatar="👤"):
                st.markdown(prompt)

        # Process the request using the LucaManager
        with messages_container:
            with st.chat_message("assistant", avatar="🤖"):
                message_placeholder = st.empty()
                # Show typing indicator
                typing_indicator = message_placeholder.container()
                typing_cols = typing_indicator.columns([0.1, 10])
                with typing_cols[0]:
                    st.markdown(
                        """<div style="display: flex; gap: 4px;">
                        <div style="width: 8px; height: 8px; background: #666; border-radius: 50%; animation: bounce 1.4s infinite;"></div>
                        <div style="width: 8px; height: 8px; background: #666; border-radius: 50%; animation: bounce 1.4s infinite 0.2s;"></div>
                        <div style="width: 8px; height: 8px; background: #666; border-radius: 50%; animation: bounce 1.4s infinite 0.4s;"></div>
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
