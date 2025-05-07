#!/usr/bin/env python3
"""Simple Filesystem MCP Server"""

import asyncio
import json
import os
from pathlib import Path
from typing import Any, Dict

from mcp.server import Server, types
from mcp.server.stdio import stdio_server


async def serve():
    """Run the Filesystem MCP server"""
    server = Server()

    @server.tool()
    async def read_file(path: str) -> str:
        """Read the contents of a file"""
        try:
            with open(path, "r", encoding="utf-8") as f:
                return f.read()
        except FileNotFoundError:
            return f"Error: File not found: {path}"
        except Exception as e:
            return f"Error reading file: {str(e)}"

    @server.tool()
    async def write_file(path: str, content: str) -> str:
        """Write content to a file"""
        try:
            # Create directories if they don't exist
            os.makedirs(os.path.dirname(path), exist_ok=True)
            with open(path, "w", encoding="utf-8") as f:
                f.write(content)
            return f"Successfully wrote to {path}"
        except Exception as e:
            return f"Error writing file: {str(e)}"

    @server.tool()
    async def list_directory(path: str = ".") -> str:
        """List the contents of a directory"""
        try:
            items = []
            for item in os.listdir(path):
                item_path = os.path.join(path, item)
                if os.path.isdir(item_path):
                    items.append(f"[DIR] {item}")
                else:
                    items.append(f"[FILE] {item}")
            return "\n".join(items)
        except Exception as e:
            return f"Error listing directory: {str(e)}"

    @server.tool()
    async def get_file_info(path: str) -> str:
        """Get information about a file or directory"""
        try:
            stat = os.stat(path)
            path_obj = Path(path)

            info = {
                "path": path,
                "name": path_obj.name,
                "is_file": path_obj.is_file(),
                "is_directory": path_obj.is_dir(),
                "size": stat.st_size,
                "modified": stat.st_mtime,
                "permissions": oct(stat.st_mode)[-3:],
            }

            return json.dumps(info, indent=2)
        except Exception as e:
            return f"Error getting file info: {str(e)}"

    @server.tool()
    async def search_files(directory: str, pattern: str) -> str:
        """Search for files matching a pattern"""
        try:
            matches = []
            for root, dirs, files in os.walk(directory):
                for file in files:
                    if pattern in file:
                        matches.append(os.path.join(root, file))

            if matches:
                return "\n".join(matches)
            else:
                return f"No files matching '{pattern}' found in {directory}"
        except Exception as e:
            return f"Error searching files: {str(e)}"

    @server.tool()
    async def create_directory(path: str) -> str:
        """Create a new directory"""
        try:
            os.makedirs(path, exist_ok=True)
            return f"Successfully created directory: {path}"
        except Exception as e:
            return f"Error creating directory: {str(e)}"

    @server.tool()
    async def delete_file(path: str) -> str:
        """Delete a file"""
        try:
            os.remove(path)
            return f"Successfully deleted: {path}"
        except FileNotFoundError:
            return f"Error: File not found: {path}"
        except Exception as e:
            return f"Error deleting file: {str(e)}"

    @server.tool()
    async def get_current_directory() -> str:
        """Get the current working directory"""
        return os.getcwd()

    @server.tool()
    async def change_directory(path: str) -> str:
        """Change the current working directory"""
        try:
            os.chdir(path)
            return f"Changed directory to: {os.getcwd()}"
        except Exception as e:
            return f"Error changing directory: {str(e)}"

    # Run the server using the stdio transport
    async with stdio_server(server):
        await asyncio.Event().wait()


if __name__ == "__main__":
    asyncio.run(serve())
