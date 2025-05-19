"""Tests to improve coverage for agent schemas."""

from luca_core.schemas.agent import Agent, AgentConfig


class TestAgentCoverage:
    """Test agent schema edge cases for coverage."""

    def test_agent_get_description(self):
        """Test get_agent_description method."""
        config = AgentConfig(
            name="TestAgent",
            role="Tester",
            description="A test agent",
            capabilities=["testing"],
            model="test-model",
            max_tasks=5,
        )

        agent = Agent(id="test-123", config=config)

        description = agent.get_agent_description()
        assert description == "TestAgent (Tester): A test agent"
