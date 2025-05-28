"""MCP Server Manager for Streamlit UI"""

import asyncio
import json
import os
import sys

# Add the parent directory to the path to import our tools
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(__file__))))

import streamlit as st  # noqa: E402

from tools.mcp_autogen_bridge import MCPAutogenBridge  # noqa: E402
from tools.mcp_client import MCPClientManager, MCPServerConfig  # noqa: E402

st.set_page_config(page_title="MCP Manager", page_icon="M", layout="wide")

# Initialize MCP client in session state
if "mcp_client" not in st.session_state:
    st.session_state.mcp_client = MCPClientManager()
    st.session_state.mcp_started = False

# Initialize bridge
if "mcp_bridge" not in st.session_state:
    st.session_state.mcp_bridge = MCPAutogenBridge(st.session_state.mcp_client)


async def start_mcp_client():
    """Start the MCP client if not already started"""
    if not st.session_state.mcp_started:
        await st.session_state.mcp_client.start()
        st.session_state.mcp_started = True


async def stop_mcp_client():
    """Stop the MCP client"""
    if st.session_state.mcp_started:
        await st.session_state.mcp_client.stop()
        st.session_state.mcp_started = False


def main():
    st.markdown("# 🔌 MCP Server Manager")
    st.markdown("Connect and manage MCP (Model Context Protocol) servers")

    # Ensure MCP client is started
    if not st.session_state.mcp_started:
        if st.button("Start MCP Client"):
            asyncio.run(start_mcp_client())
            st.rerun()
        return

    # Create tabs for different MCP management functions
    tabs = st.tabs(["Connected Servers", "Add Server", "Available Tools", "Test Tools"])

    # Tab 1: Connected Servers
    with tabs[0]:
        st.header("Connected MCP Servers")

        # Get connected servers
        connected_servers = st.session_state.mcp_client.get_connected_servers()

        if not connected_servers:
            st.info("No MCP servers currently connected.")
        else:
            for server in connected_servers:
                with st.expander(f"{server.name}"):
                    col1, col2 = st.columns([3, 1])

                    with col1:
                        st.markdown(f"**Type:** {server.type}")
                        if server.script_path:
                            st.markdown(f"**Script:** `{server.script_path}`")
                        if server.url:
                            st.markdown(f"**URL:** {server.url}")
                        if server.description:
                            st.markdown(f"**Description:** {server.description}")

                        # Show tools for this server
                        tools = st.session_state.mcp_client.get_server_tools(
                            server.name
                        )
                        st.markdown(f"**Tools:** {len(tools)}")
                        for tool in tools:
                            st.markdown(f"  - `{tool.name}`: {tool.description}")

                    with col2:
                        if st.button("Disconnect", key=f"disconnect_{server.name}"):
                            asyncio.run(
                                st.session_state.mcp_client.disconnect_from_server(
                                    server.name
                                )
                            )
                            st.rerun()

    # Tab 2: Add Server
    with tabs[1]:
        st.header("Add New MCP Server")

        with st.form("add_server_form"):
            server_name = st.text_input("Server Name", placeholder="e.g., filesystem")
            server_type = st.selectbox("Server Type", ["stdio", "http"])

            if server_type == "stdio":
                script_path = st.text_input(
                    "Script Path", placeholder="/path/to/server_script.py"
                )
                url = None
            else:
                script_path = None
                url = st.text_input("Server URL", placeholder="http://localhost:8080")

            description = st.text_area("Description (optional)")

            submitted = st.form_submit_button("Connect to Server")

            if submitted:
                config = MCPServerConfig(
                    name=server_name,
                    type=server_type,
                    script_path=script_path,
                    url=url,
                    description=description,
                )

                # Connect to the server
                async def connect():
                    success = await st.session_state.mcp_client.connect_to_server(
                        config
                    )
                    if success:
                        st.success(f"Successfully connected to {server_name}")
                    else:
                        st.error(f"Failed to connect to {server_name}")

                asyncio.run(connect())
                st.rerun()

    # Tab 3: Available Tools
    with tabs[2]:
        st.header("Available Tools")

        # Get all tools
        tools = asyncio.run(st.session_state.mcp_client.list_available_tools())

        if not tools:
            st.info("No tools available. Connect to an MCP server first.")
        else:
            # Group tools by server
            tools_by_server = {}
            for tool in tools:
                if tool.server_name not in tools_by_server:
                    tools_by_server[tool.server_name] = []
                tools_by_server[tool.server_name].append(tool)

            # Display tools by server
            for server_name, server_tools in tools_by_server.items():
                st.markdown(
                    f'<h3 style="color: #8b5cf6; margin-top: 1.5rem;">{server_name}</h3>',
                    unsafe_allow_html=True,
                )

                for tool in server_tools:
                    with st.expander(f"{tool.name}"):
                        st.markdown(f"**Description:** {tool.description}")

                        # Show the tool schema
                        if tool.schema:
                            st.markdown("**Parameters:**")
                            st.json(tool.schema)

    # Tab 4: Test Tools
    with tabs[3]:
        st.header("Test Tool Execution")

        # Get all tools
        tools = asyncio.run(st.session_state.mcp_client.list_available_tools())

        if not tools:
            st.info("No tools available. Connect to an MCP server first.")
        else:
            # Select tool to test
            tool_names = [f"{tool.server_name}.{tool.name}" for tool in tools]
            selected_tool = st.selectbox("Select Tool", tool_names)

            if selected_tool:
                # Find the selected tool
                tool = None
                for t in tools:
                    if f"{t.server_name}.{t.name}" == selected_tool:
                        tool = t
                        break

                if tool:
                    st.markdown(f"**Description:** {tool.description}")

                    # Show tool schema
                    if tool.schema and tool.schema.get("properties"):
                        st.markdown("**Parameters:**")

                        # Create input fields based on schema
                        parameters = {}
                        for param_name, param_info in tool.schema["properties"].items():
                            param_type = param_info.get("type", "string")
                            param_desc = param_info.get("description", "")

                            if param_type == "string":
                                parameters[param_name] = st.text_input(
                                    param_name, help=param_desc
                                )
                            elif param_type == "number":
                                parameters[param_name] = st.number_input(
                                    param_name, help=param_desc
                                )
                            elif param_type == "boolean":
                                parameters[param_name] = st.checkbox(
                                    param_name, help=param_desc
                                )
                    else:
                        # Manual JSON input if no schema
                        json_input = st.text_area(
                            "Parameters (JSON)",
                            value="{}",
                            help="Enter tool parameters as JSON",
                        )
                        try:
                            parameters = json.loads(json_input)
                        except json.JSONDecodeError:
                            st.error("Invalid JSON format")
                            parameters = None

                    # Execute tool button
                    if st.button("Execute Tool"):
                        if parameters is not None:
                            try:
                                # Execute the tool
                                with st.spinner("Executing tool..."):
                                    result = asyncio.run(
                                        st.session_state.mcp_client.execute_tool(
                                            selected_tool, parameters
                                        )
                                    )

                                st.success("Tool executed successfully!")
                                st.markdown("**Result:**")
                                st.text_area("Output", value=str(result), height=200)

                            except Exception as e:
                                st.error(f"Error executing tool: {str(e)}")

    # Footer with controls
    st.divider()
    col1, col2, col3 = st.columns([1, 1, 1])

    with col1:
        if st.button("Stop MCP Client"):
            asyncio.run(stop_mcp_client())
            st.rerun()

    with col2:
        if st.button("Refresh"):
            st.rerun()

    with col3:
        # Export connected servers
        if st.button("Export Config"):
            config = {
                "servers": [
                    {
                        "name": s.name,
                        "type": s.type,
                        "script_path": s.script_path,
                        "url": s.url,
                        "description": s.description,
                    }
                    for s in st.session_state.mcp_client.get_connected_servers()
                ]
            }
            st.download_button(
                "Download Config",
                json.dumps(config, indent=2),
                "mcp_config.json",
                "application/json",
            )


if __name__ == "__main__":
    main()
