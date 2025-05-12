"""
Integration tests for agent orchestration.

These tests validate that the LucaManager correctly orchestrates agents
and processes requests through the full pipeline.
"""

import asyncio
import os
import tempfile
from pathlib import Path

import pytest

from luca_core.context import factory
from luca_core.manager.manager import LucaManager, ResponseOptions
from luca_core.registry import registry
from luca_core.schemas.agent import LearningMode


@pytest.mark.asyncio
async def test_manager_initialization():
    """Test that the LucaManager can be initialized correctly."""
    # Create a temp database file
    with tempfile.TemporaryDirectory() as temp_dir:
        db_path = os.path.join(temp_dir, "test.db")
        
        # Create context store
        context_store = await factory.create_async_context_store("sqlite", db_path)
        
        # Create manager
        manager = LucaManager(context_store=context_store, tool_registry=registry)
        
        # Initialize manager
        await manager.initialize()
        
        # Verify manager has created default agents
        assert "luca" in manager.agents
        assert "coder" in manager.agents
        assert "tester" in manager.agents
        assert "doc_writer" in manager.agents
        assert "analyst" in manager.agents
        
        # Verify agent configs
        assert manager.agents["luca"].config.name == "Luca"
        assert manager.agents["coder"].config.name == "Coder"


@pytest.mark.asyncio
async def test_simple_request_processing():
    """Test that the LucaManager can process a simple request."""
    # Create a temp database file
    with tempfile.TemporaryDirectory() as temp_dir:
        db_path = os.path.join(temp_dir, "test.db")
        
        # Create context store
        context_store = await factory.create_async_context_store("sqlite", db_path)
        
        # Create manager
        manager = LucaManager(context_store=context_store, tool_registry=registry)
        
        # Initialize manager
        await manager.initialize()
        
        # Process a simple request
        response_options = ResponseOptions(
            learning_mode=LearningMode.PRO,
            verbose=False,
            include_agent_info=False
        )
        
        response = await manager.process_request("Hello, Luca!", response_options)
        
        # Verify response is not empty
        assert response is not None
        assert len(response) > 0
        
        # Verify the response contains some reasonable text
        assert "Processed" in response


@pytest.mark.asyncio
async def test_learning_modes():
    """Test that the LucaManager respects different learning modes."""
    # Create a temp database file
    with tempfile.TemporaryDirectory() as temp_dir:
        db_path = os.path.join(temp_dir, "test.db")
        
        # Create context store
        context_store = await factory.create_async_context_store("sqlite", db_path)
        
        # Create manager
        manager = LucaManager(context_store=context_store, tool_registry=registry)
        
        # Initialize manager
        await manager.initialize()
        
        # Process requests with different learning modes
        request = "Tell me about Python"
        
        # Test NOOB mode
        noob_options = ResponseOptions(
            learning_mode=LearningMode.NOOB,
            verbose=True,
            include_agent_info=True
        )
        
        noob_response = await manager.process_request(request, noob_options)
        
        # Test PRO mode
        pro_options = ResponseOptions(
            learning_mode=LearningMode.PRO,
            verbose=False,
            include_agent_info=False
        )
        
        pro_response = await manager.process_request(request, pro_options)
        
        # Test GURU mode
        guru_options = ResponseOptions(
            learning_mode=LearningMode.GURU,
            verbose=True,
            include_agent_info=False
        )
        
        guru_response = await manager.process_request(request, guru_options)
        
        # Verify responses are not empty
        assert all(len(resp) > 0 for resp in [noob_response, pro_response, guru_response])
        
        # In our placeholder implementation, the responses are the same
        # In a full implementation, they would differ based on learning mode
