"""Tests to improve coverage for agent schemas."""

from luca_core.schemas.agent import (
    Agent,
    AgentCapability,
    AgentConfig,
    AgentRole,
    LLMModelConfig,
)


class TestAgentCoverage:
    """Test agent schema edge cases for coverage."""

    def test_agent_get_description(self):
        """Test get_agent_description method."""
        llm_config = LLMModelConfig(model_name="test-model")

        config = AgentConfig(
            id="test-agent-id",
            name="TestAgent",
            role=AgentRole.TESTER,
            description="A test agent",
            llm_config=llm_config,
            system_prompt="You are a test agent",
            capabilities=[AgentCapability.TESTING],
            max_consecutive_auto_reply=5,
        )

        agent = Agent(config=config)

        description = agent.get_agent_description()
        assert description == f"TestAgent ({AgentRole.TESTER}): A test agent"
