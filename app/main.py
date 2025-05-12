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
    page_title="Luca Dev Assistant",
    page_icon="🧠",
    layout="wide",
    initial_sidebar_state="expanded",
)

# Custom CSS for styling
st.markdown(
    """
<style>
    .main-header {
        font-size: 2.5rem;
        font-weight: bold;
        color: #1E88E5;
        text-align: center;
        margin-bottom: 2rem;
    }
    .agent-container {
        background-color: #f8f9fa;
        border-radius: 10px;
        padding: 1rem;
        margin: 1rem 0;
    }
    .status-active {
        color: #4CAF50;
    }
    .status-idle {
        color: #FFC107;
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
    st.markdown(
        "<h1 class='main-header'>💼 Luca Dev Assistant</h1>", unsafe_allow_html=True
    )

    # Sidebar navigation
    with st.sidebar:
        st.header("🔧 Navigation")
        st.page_link("main.py", label="💬 Chat", icon="💬")
        st.page_link("pages/agent_manager.py", label="🌳 Agent Manager", icon="🤖")
        st.page_link("pages/mcp_manager.py", label="🔌 MCP Manager", icon="🔌")

        st.divider()

        # Learning mode selector
        st.header("🧠 Learning Mode")
        current_mode = get_learning_mode()
        mode_descriptions = {
            LearningMode.NOOB: "Detailed explanations for beginners",
            LearningMode.PRO: "Concise responses for experienced developers",
            LearningMode.GURU: "Deep technical insights and explanations",
        }

        mode = st.selectbox(
            "Select Mode",
            options=[LearningMode.NOOB, LearningMode.PRO, LearningMode.GURU],
            format_func=lambda x: f"{x.title()} - {mode_descriptions[x]}",
            index=[LearningMode.NOOB, LearningMode.PRO, LearningMode.GURU].index(
                current_mode
            ),
        )
        if mode != current_mode:
            set_learning_mode(mode)
            st.rerun()

        st.divider()

        # Quick stats
        st.header("📊 Quick Stats")
        col1, col2 = st.columns(2)
        with col1:
            st.metric("Active Agents", "1")
        with col2:
            st.metric("Tasks Queue", "0")

    # Main chat interface
    st.header("💬 Chat with Luca")

    # Initialize chat history
    if "messages" not in st.session_state:
        st.session_state.messages = [
            {
                "role": "assistant",
                "content": (
                    "👋 Hello! I'm Luca, your AI development assistant. "
                    "I specialize in QuantConnect strategies and full-stack "
                    "development. How can I help you today?"
                ),
            }
        ]

    # Display chat history
    for message in st.session_state.messages:
        with st.chat_message(message["role"]):
            st.markdown(message["content"])

    # Chat input
    if prompt := st.chat_input("Ask Luca anything..."):
        # Add user message to chat history
        st.session_state.messages.append({"role": "user", "content": prompt})
        with st.chat_message("user"):
            st.markdown(prompt)

        # Process the request using the LucaManager
        with st.chat_message("assistant"):
            message_placeholder = st.empty()
            with st.spinner("Luca is thinking..."):
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
                    message_placeholder.markdown(error_msg)
                    st.session_state.messages.append(
                        {"role": "assistant", "content": error_msg}
                    )

    # Footer
    st.divider()
    st.caption("Built with ❤️ using Streamlit | Luca Dev Assistant v0.1.0")


if __name__ == "__main__":
    main()
