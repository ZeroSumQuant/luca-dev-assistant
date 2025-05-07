import json

import graphviz
import streamlit as st

st.set_page_config(page_title="Agent Manager", page_icon="🤖", layout="wide")

# Agent configuration with model selections
DEFAULT_AGENT_CONFIG = {
    "luca": {
        "name": "Luca",
        "role": "Manager",
        "description": "Main orchestration agent that coordinates all tasks",
        "model": "gpt-4o",
        "available_models": ["gpt-4o", "claude-3-sonnet", "gpt-3.5-turbo"],
        "status": "active",
        "color": "#1E88E5",
    },
    "coder": {
        "name": "Coder",
        "role": "Developer",
        "description": "Specialist agent for writing and refactoring code",
        "model": "gpt-4",
        "available_models": [
            "gpt-4",
            "claude-3-opus",
            "gpt-3.5-turbo",
            "deepseek-coder",
        ],
        "status": "idle",
        "color": "#4CAF50",
    },
    "tester": {
        "name": "Tester",
        "role": "QA Engineer",
        "description": "Runs tests, validates code quality, and ensures functionality",
        "model": "gpt-3.5-turbo",
        "available_models": ["gpt-3.5-turbo", "gpt-4", "claude-3-haiku"],
        "status": "idle",
        "color": "#FF9800",
    },
    "doc_writer": {
        "name": "Doc Writer",
        "role": "Technical Writer",
        "description": "Creates documentation, README files, and API docs",
        "model": "claude-3-sonnet",
        "available_models": ["claude-3-sonnet", "gpt-4", "claude-3-haiku"],
        "status": "idle",
        "color": "#9C27B0",
    },
    "analyst": {
        "name": "Analyst",
        "role": "QuantConnect Specialist",
        "description": "Analyzes market data and creates trading strategies",
        "model": "gpt-4o",
        "available_models": ["gpt-4o", "claude-3-opus", "gpt-4-turbo"],
        "status": "idle",
        "color": "#F44336",
    },
}

# Initialize session state for agent config
if "agent_config" not in st.session_state:
    st.session_state.agent_config = DEFAULT_AGENT_CONFIG.copy()


def create_agent_tree() -> graphviz.Digraph:
    """Create a graphviz visualization of the agent hierarchy."""
    dot = graphviz.Digraph(comment="Agent Tree")
    dot.attr(rankdir="TB", bgcolor="transparent")
    dot.attr("node", style="filled", fontsize="12", fontname="Arial")

    # Add nodes
    for agent_id, agent_info in st.session_state.agent_config.items():
        dot.node(
            agent_id,
            f"{agent_info['name']}\n{agent_info['model']}",
            fillcolor=agent_info["color"],
            fontcolor="white" if agent_id == "luca" else "black",
        )

    # Add edges (manager relationships)
    for agent_id in st.session_state.agent_config:
        if agent_id != "luca":
            dot.edge("luca", agent_id)

    return dot


def main():
    st.markdown("# 🌳 Agent Manager")
    st.markdown("Configure and monitor your agent team structure")

    # Create tabs
    tabs = st.tabs(["🌳 Agent Tree", "⚙️ Configure Agents", "📊 Agent Status"])

    # Tab 1: Agent Tree Visualization
    with tabs[0]:
        st.header("Agent Hierarchy")

        # Generate and display the tree
        try:
            dot = create_agent_tree()
            st.graphviz_chart(dot.source)
        except Exception as e:
            st.error(f"Error creating tree visualization: {str(e)}")
            st.write("Fallback: Using text representation")

            # Fallback text representation
            st.markdown("```")
            st.markdown("🧠 Luca (Manager)")
            st.markdown("├── 💻 Coder")
            st.markdown("├── 🧪 Tester")
            st.markdown("├── 📝 Doc Writer")
            st.markdown("└── 📈 Analyst")
            st.markdown("```")

    # Tab 2: Configure Agents
    with tabs[1]:
        st.header("Agent Configuration")

        # Agent selection
        cols = st.columns(3)
        with cols[0]:
            selected_agent = st.selectbox(
                "Select Agent to Configure",
                options=list(st.session_state.agent_config.keys()),
                format_func=lambda x: st.session_state.agent_config[x]["name"],
            )

        if selected_agent:
            agent_info = st.session_state.agent_config[selected_agent]

            # Agent details
            with st.container():
                col1, col2 = st.columns([1, 2])

                with col1:
                    st.markdown(f"### {agent_info['name']}")
                    st.markdown(f"**Role:** {agent_info['role']}")
                    st.markdown(f"**Status:** {agent_info['status'].title()}")

                with col2:
                    st.markdown("### Description")
                    st.markdown(agent_info["description"])

                    # Model selection
                    st.markdown("### Model Configuration")
                    new_model = st.selectbox(
                        "Select Model",
                        options=agent_info["available_models"],
                        index=agent_info["available_models"].index(agent_info["model"]),
                    )

                    if new_model != agent_info["model"]:
                        if st.button("Update Model"):
                            st.session_state.agent_config[selected_agent][
                                "model"
                            ] = new_model
                            st.success(
                                f"Updated {agent_info['name']}'s model to {new_model}"
                            )
                            st.rerun()

    # Tab 3: Agent Status
    with tabs[2]:
        st.header("Agent Status Dashboard")

        # Create status cards
        cols = st.columns(3)
        for i, (agent_id, agent_info) in enumerate(
            st.session_state.agent_config.items()
        ):
            with cols[i % 3]:
                with st.container():
                    st.markdown(f"### {agent_info['name']}")
                    st.markdown(f"**Model:** `{agent_info['model']}`")

                    # Status indicator
                    if agent_info["status"] == "active":
                        st.success("🟢 Active")
                    else:
                        st.warning("🟡 Idle")

                    # Quick stats (mock data for MVP)
                    col1, col2 = st.columns(2)
                    with col1:
                        st.metric("Tasks", "0")
                    with col2:
                        st.metric("Success Rate", "100%")

                    st.divider()

    # Footer controls
    st.divider()
    col1, col2, col3 = st.columns([1, 1, 1])

    with col1:
        if st.button("🔄 Reset to Defaults"):
            st.session_state.agent_config = DEFAULT_AGENT_CONFIG.copy()
            st.success("Configuration reset to defaults")
            st.rerun()

    with col2:
        # Export configuration
        if st.button("📥 Export Config"):
            config_json = json.dumps(st.session_state.agent_config, indent=2)
            st.download_button(
                "Download Config", config_json, "agent_config.json", "application/json"
            )

    with col3:
        # Apply changes
        if st.button("✅ Apply Changes"):
            st.success("Agent configuration applied successfully!")
            # TODO: Implement actual agent configuration update


if __name__ == "__main__":
    main()
