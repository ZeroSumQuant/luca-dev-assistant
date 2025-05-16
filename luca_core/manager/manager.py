"""LUCA Manager implementation.

This module provides the core orchestration layer that connects all components
and implements the main LUCA functionality.
"""

import asyncio
import logging
import uuid
from datetime import datetime
from typing import Any, Dict, List, Optional, Union

from pydantic import BaseModel

from luca_core.context import BaseContextStore
from luca_core.error import ErrorHandler, error_handler, handle_exceptions
from luca_core.registry import ToolRegistry, registry
from luca_core.schemas import (
    Agent,
    AgentConfig,
    AgentRole,
    AgentStatus,
    ClarificationRequest,
    ErrorCategory,
    ErrorPayload,
    ErrorSeverity,
    LearningMode,
    LLMModelConfig,
    Message,
    MessageRole,
    MetricRecord,
    Project,
    Task,
    TaskResult,
    TaskStatus,
    create_system_error,
    create_user_error,
)

logger = logging.getLogger(__name__)


class ResponseOptions(BaseModel):
    """Options for response generation."""

    learning_mode: LearningMode = LearningMode.PRO
    verbose: bool = False
    include_agent_info: bool = False
    format: str = "markdown"


class LucaManager:
    """Core orchestration manager for LUCA.

    The manager coordinates all components and implements the main LUCA functionality.
    """

    def __init__(
        self,
        context_store: BaseContextStore,
        tool_registry: Optional[ToolRegistry] = None,
        error_handler: Optional[ErrorHandler] = None,
    ):
        """Initialize the LUCA manager.

        Args:
            context_store: Context store for persistent memory
            tool_registry: Tool registry for tool management (defaults to global registry)
            error_handler: Error handler for error management (defaults to global handler)
        """
        self.context_store = context_store
        self.tool_registry = tool_registry or registry
        self.error_handler = error_handler or error_handler
        self.agents: Dict[str, Agent] = {}
        self.current_project: Optional[Project] = None
        self.user_id = "default"

    async def initialize(self) -> None:
        """Initialize the manager and load default agents."""
        # Load user preferences
        preferences = await self.context_store.get_user_preferences(self.user_id)

        # Create default agents if not already registered
        await self._create_default_agents()

        # Load active project if any
        # This is a placeholder for project loading logic
        pass

    async def _create_default_agents(self) -> None:
        """Create default agents if they don't exist."""
        # LUCA Manager agent
        manager_config = AgentConfig(
            id="luca",
            name="Luca",
            role=AgentRole.MANAGER,
            description="Main orchestration agent that coordinates all tasks",
            llm_config=LLMModelConfig(
                model_name="gpt-4o",
                temperature=0.2,
            ),
            system_prompt="You are Luca, the AutoGen development assistant...",
            capabilities=[],
            tools=[],
        )

        manager_agent = Agent(
            config=manager_config,
            status=AgentStatus.IDLE,
        )

        # Coder agent
        coder_config = AgentConfig(
            id="coder",
            name="Coder",
            role=AgentRole.CODER,
            description="Specialist agent for writing and refactoring code",
            llm_config=LLMModelConfig(
                model_name="gpt-4",
                temperature=0.1,
            ),
            system_prompt="You are a coding specialist...",
            capabilities=[],
            tools=[
                "file_io.read_text",
                "file_io.write_text",
                "git_tools.get_git_diff",
            ],
        )

        coder_agent = Agent(
            config=coder_config,
            status=AgentStatus.IDLE,
        )

        # Tester agent
        tester_config = AgentConfig(
            id="tester",
            name="Tester",
            role=AgentRole.TESTER,
            description="Specialist agent for testing and quality assurance",
            llm_config=LLMModelConfig(
                model_name="gpt-4",
                temperature=0.2,
            ),
            system_prompt="You are a testing specialist...",
            capabilities=[],
            tools=[
                "file_io.read_text",
            ],
        )

        tester_agent = Agent(
            config=tester_config,
            status=AgentStatus.IDLE,
        )

        # Doc Writer agent
        doc_writer_config = AgentConfig(
            id="doc_writer",
            name="Doc Writer",
            role=AgentRole.DOC_WRITER,
            description="Specialist agent for creating documentation",
            llm_config=LLMModelConfig(
                model_name="gpt-4",
                temperature=0.3,
            ),
            system_prompt="You are a documentation specialist...",
            capabilities=[],
            tools=[
                "file_io.read_text",
                "file_io.write_text",
            ],
        )

        doc_writer_agent = Agent(
            config=doc_writer_config,
            status=AgentStatus.IDLE,
        )

        # Analyst agent
        analyst_config = AgentConfig(
            id="analyst",
            name="Analyst",
            role=AgentRole.ANALYST,
            description="Specialist agent for analyzing data and QuantConnect strategies",
            llm_config=LLMModelConfig(
                model_name="gpt-4o",
                temperature=0.2,
            ),
            system_prompt="You are a data analysis and QuantConnect specialist...",
            capabilities=[],
            tools=[
                "file_io.read_text",
            ],
        )

        analyst_agent = Agent(
            config=analyst_config,
            status=AgentStatus.IDLE,
        )

        # Register all agents
        self.agents["luca"] = manager_agent
        self.agents["coder"] = coder_agent
        self.agents["tester"] = tester_agent
        self.agents["doc_writer"] = doc_writer_agent
        self.agents["analyst"] = analyst_agent

        logger.info("Default agents created and registered")

    async def process_request(
        self, request: str, response_options: Optional[ResponseOptions] = None
    ) -> str:
        """Process a user request through the full orchestration loop.

        Args:
            request: User request text
            response_options: Options for response generation

        Returns:
            Response text
        """
        # Use default response options if not provided
        response_options = response_options or ResponseOptions()

        # Create a message for the request
        message_id = str(uuid.uuid4())
        message = Message(
            id=message_id,
            role=MessageRole.USER,
            content=request,
        )

        # Store the message
        await self.context_store.store_message(message)

        # Step 1: Understand the request
        understood_request = await self._understand(request)

        # Step 2: Create a plan
        plan = await self._create_plan(understood_request)

        # Step 3: Select a team
        team = await self._select_team(plan)

        # Step 4: Delegate tasks
        results = await self._delegate_tasks(team, plan)

        # Step 5: Aggregate results
        response = await self._aggregate_results(results, response_options)

        # Create a message for the response
        response_message = Message(
            id=str(uuid.uuid4()),
            role=MessageRole.ASSISTANT,
            content=response,
            metadata={
                "request_id": message_id,
                "learning_mode": response_options.learning_mode,
            },
        )

        # Store the response message
        await self.context_store.store_message(response_message)

        # Record metrics
        await self._record_metrics(request, response, response_options)

        return response

    async def _understand(self, request: str) -> Dict[str, Any]:
        """Understand the user request.

        This analyzes the request to extract intent, domain, and other information.

        Args:
            request: User request text

        Returns:
            Dictionary with extracted information
        """
        # This is a placeholder for more sophisticated understanding logic
        # In Phase 0, we'll use a simple approach

        return {
            "text": request,
            "domain": "general",
            "intent": "unknown",
            "complexity": "medium",
        }

    async def _create_plan(
        self, understood_request: Dict[str, Any]
    ) -> List[Dict[str, Any]]:
        """Create a plan based on the understood request.

        Args:
            understood_request: Output from the understanding step

        Returns:
            List of planned tasks
        """
        # This is a placeholder for more sophisticated planning logic
        # In Phase 0, we'll use a simple approach

        return [
            {
                "id": str(uuid.uuid4()),
                "description": understood_request["text"],
                "agent": "luca",
                "priority": 1,
            }
        ]

    async def _select_team(self, plan: List[Dict[str, Any]]) -> List[Agent]:
        """Select a team of agents based on the plan.

        Args:
            plan: List of planned tasks

        Returns:
            List of selected agents
        """
        # This is a placeholder for more sophisticated team selection logic
        # In Phase 0, we'll always use the LUCA agent

        return [self.agents["luca"]]

    async def _delegate_tasks(
        self, team: List[Agent], plan: List[Dict[str, Any]]
    ) -> List[TaskResult]:
        """Delegate tasks to the selected team of agents.

        Args:
            team: List of agents
            plan: List of planned tasks

        Returns:
            List of task results
        """
        # This is a placeholder for more sophisticated task delegation logic
        # In Phase 0, we'll use a simple approach

        results = []

        for task_info in plan:
            # Create a formal task record
            task = Task(
                id=task_info["id"],
                agent_id=task_info["agent"],
                description=task_info["description"],
                status=TaskStatus.PENDING,
            )

            # Store the task
            await self.context_store.store_task(task)

            # Update agent status
            agent = self.agents[task_info["agent"]]
            agent.status = AgentStatus.BUSY
            agent.current_task_id = task.id

            # Execute the task (placeholder for actual agent execution)
            result = TaskResult(
                task_id=task.id,
                success=True,
                result=f"Processed: {task.description}",
                execution_time_ms=100,
            )

            # Update agent status
            agent.status = AgentStatus.IDLE
            agent.current_task_id = None
            agent.total_tasks_completed += 1
            agent.task_history.append(task.id)

            # Store the result
            await self.context_store.store_task_result(result)

            results.append(result)

        return results

    async def _aggregate_results(
        self, results: List[TaskResult], options: ResponseOptions
    ) -> str:
        """Aggregate results from multiple tasks into a coherent response.

        Args:
            results: List of task results
            options: Response options

        Returns:
            Aggregated response text
        """
        # This is a placeholder for more sophisticated result aggregation logic
        # In Phase 0, we'll use a simple approach

        if not results:
            return "I couldn't process your request. Please try again."

        # For now, just concatenate all results
        combined_result = "\n\n".join(r.result for r in results if r.success)

        if not combined_result:
            return "I processed your request, but encountered errors and couldn't produce results."

        return combined_result

    async def _record_metrics(
        self, request: str, response: str, options: ResponseOptions
    ) -> None:
        """Record metrics for the request-response cycle.

        Args:
            request: User request text
            response: Response text
            options: Response options
        """
        # This is a placeholder for more sophisticated metrics recording
        # In Phase 0, we'll just log the metrics

        logger.info(
            f"Processed request of length {len(request)} in learning mode {options.learning_mode}"
        )

        # In a more advanced implementation, we would store metrics in the context store
