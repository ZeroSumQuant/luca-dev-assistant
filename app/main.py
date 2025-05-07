import streamlit as st
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Configure the page
st.set_page_config(
    page_title="Luca Dev Assistant",
    page_icon="🧠",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS for styling
st.markdown("""
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
""", unsafe_allow_html=True)

def main():
    st.markdown("<h1 class='main-header'>💼 Luca Dev Assistant</h1>", unsafe_allow_html=True)
    
    # Sidebar navigation
    with st.sidebar:
        st.header("🔧 Navigation")
        st.page_link("main.py", label="💬 Chat", icon="💬")
        st.page_link("pages/agent_manager.py", label="🌳 Agent Manager", icon="🤖")
        
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
        st.session_state.messages = [{
            "role": "assistant",
            "content": "👋 Hello! I'm Luca, your AI development assistant. I specialize in QuantConnect strategies and full-stack development. How can I help you today?"
        }]
    
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
        
        # TODO: Replace with actual agent call
        with st.chat_message("assistant"):
            message_placeholder = st.empty()
            with st.spinner("Luca is thinking..."):
                # Simulate streaming response
                full_response = f"You asked: '{prompt}'\n\nI'm currently in MVP mode. The agent orchestration will be implemented to handle your request."
                message_placeholder.markdown(full_response)
                
                # Add assistant response to chat history
                st.session_state.messages.append({"role": "assistant", "content": full_response})
    
    # Footer
    st.divider()
    st.caption("Built with ❤️ using Streamlit | Luca Dev Assistant v0.1.0")

if __name__ == "__main__":
    main()
