# LUCA Agent Orchestration Architecture

This document outlines the architecture for LUCA's agent orchestration system, defining the core components, implementation phases, and how agents interact to fulfill user requests. The architecture prioritizes robustness, resilience, and a solid foundation before advanced features.

## 1. Core Skeleton Components

LUCA's agent orchestration is built on four essential primitives that form the foundation of the entire system:

### 1.1 ContextStore

**Purpose**: Persistent shared memory across conversations and sessions.

**Key Components**:
- Conversation history storage
- Project state tracking
- Agent execution history
- User preferences and settings

**Implementation**:
- Initially SQLite-based for zero-config, ACID compliance
- Interface abstraction to allow future backend swapping (Chroma, Postgres)
- Session restoration capability for crash recovery
- Audit trail for compliance and debugging

**Schema Ownership**:
- All Pydantic models are defined in the `luca_core/schemas/` package
- These schemas are imported by all components (including MCP servers)
- This ensures consistency and prevents duplicate definitions
- Core models include: `Message`, `Task`, `TaskResult`, `ClarificationRequest`, `MetricRecord`, `Project`, `UserPreferences`

**Why Indispensable**:
- Enables intelligent routing by maintaining conversation context
- Provides crash survivability to restore work exactly where it left off
- Creates an audit trail for compliance and future "Ticket" feature
- Reduces token usage by avoiding context re-inference

### 1.2 ToolRegistry

**Purpose**: Central source of truth for all agent capabilities.

**Key Components**:
- Tool metadata and versioning
- Sandboxing and permission boundaries
- Capability categorization and tagging
- Version pinning for reproducibility

**Implementation**:
- Registry pattern with registration/discovery mechanisms
- Tool capability documentation and schema
- Sandboxing scope definitions
- Domain and task tagging system

**Why Indispensable**:
- Establishes sandbox boundaries for security
- Enables deterministic planning by agents
- Provides versioning for reproducible execution
- Facilitates MCP integration and dynamic tool discovery

### 1.3 Error-Payload Schema

**Purpose**: Standardized approach to error handling across all components.

**Key Components**:
- Uniform error structure with severity levels
- Error categorization (user error, system error, authentication, etc.)
- Recovery suggestion mechanism
- Context tracking for error origin

**Implementation**:
- Four-field schema covering 95% of failure scenarios
- Standardized error codes and categories
- Recovery hint mechanism
- Error tracing for deeper diagnostics

```python
class ErrorPayload(BaseModel):
    category: Literal["user_error", "system_error", "auth_error", 
                     "resource_error", "timeout_error"]
    severity: Literal["info", "warning", "error", "critical"]
    message: str
    context: Dict[str, Any] = {}
    recovery_hint: Optional[str] = None
```

**Why Indispensable**:
- Enables predictable recovery patterns
- Provides transparency for users
- Creates uniform telemetry for monitoring
- Simplifies manager logic for error handling

### 1.4 LucaManager

**Purpose**: Thin coordination layer that connects all components.

**Key Components**:
- Request parsing and understanding
- Task planning and delegation
- Specialist agent coordination
- Result aggregation and response generation

**Implementation**:
- Core loop: parse → plan → delegate → aggregate
- Minimal dependencies beyond the other three primitives
- Clean interfaces for extensibility
- Basic retry and error handling logic

**Why Indispensable**:
- Connects all primitives into a working system
- Provides end-to-end validation of architecture
- Keeps core functionality lean to find design flaws early
- Forms the foundation for more complex features

## 2. Implementation Phases

The implementation follows a phased approach, focusing on establishing a solid foundation before adding advanced features:

### 2.1 Phase 0 - Core Skeleton

Focus on implementing the four primitive components with comprehensive unit tests:
- ContextStore with basic persistence
- ToolRegistry with sandbox boundaries
- Error-Payload Schema implementation
- LucaManager v0 with minimal viable orchestration

Success criteria: Basic "parse → plan → delegate → aggregate" loop works reliably for simple tasks.

### 2.2 Phase 1 - Core Polish

Add essential developer ergonomics without changing core architecture:
- YAML configuration loader
- Streamlit status panels
- Basic authentication and session management
- Improved logging and monitoring

Success criteria: Developers can effectively dog-food the system and track agent activity.

### 2.3 Phase 2 - Domain Adapters

Introduce domain-specific functionality, with focus on QuantConnect:
- QuantConnect API integration
- Lean Cloud back-test integration with Tester agent
- Domain-specific tool registration
- Enhanced domain recognition

Success criteria: System can handle domain-specific tasks with appropriate specialists and tools.

### 2.4 Phase 3 - UX Enhancements

Add user experience improvements leveraging the stable foundation:
- Learning mode implementation (Noob, Pro, Guru)
- Dynamic response formatting
- Agent visualization enhancements
- User preference management

Success criteria: System adapts its communication style based on user preferences and provides clear visibility into agent activities.

### 2.5 Phase 4 - MCP Integration

Expand functionality through external Model Context Protocol servers:
- HTTP connection support
- Authentication for external servers
- Failure recovery for network issues
- Dynamic server discovery and registration

Success criteria: System reliably integrates with external MCP servers with proper error handling.

## 3. Agent Hierarchy and Communication

Building on the foundational components, LUCA implements a hierarchical agent structure:

```
                       ┌─────────────┐
                       │    LUCA     │
                       │  (Manager)  │
                       └──────┬──────┘
                              │
           ┌─────────────┬────┼────┬─────────────┐
           │             │         │             │
  ┌────────▼─────┐ ┌─────▼────┐ ┌──▼──────┐ ┌────▼─────────┐
  │    Coder     │ │  Tester  │ │   Doc   │ │   Analyst    │
  │ (Developer)  │ │   (QA)   │ │ Writer  │ │(QuantConnect)│
  └──────────────┘ └──────────┘ └─────────┘ └──────────────┘
```

### 3.1 Communication Flow

1. **Request Processing**
   - User request is captured and stored in ContextStore
   - LucaManager analyzes request for intent and domain
   - ToolRegistry is consulted to identify required capabilities

2. **Specialist Selection**
   - LucaManager determines which specialists are needed
   - Selection is based on required tools and domain expertise
   - ContextStore provides additional context from previous interactions

3. **Task Execution**
   - LucaManager delegates specific tasks to specialists
   - Specialists use ToolRegistry to access required tools
   - Results and errors are formatted according to standard schemas
   - Execution history is recorded in ContextStore

4. **Error Handling**
   - Errors are captured in the standard Error-Payload Schema
   - LucaManager determines appropriate recovery strategy
   - ContextStore is consulted for previous attempts and context
   - Error information is presented to user when appropriate

5. **Response Generation**
   - Results from specialists are aggregated by LucaManager
   - ContextStore is updated with final results
   - Response is formatted based on user preferences and learning mode
   - Complete interaction is logged for audit and improvement

## 4. Intelligent Agent Selection

Agent selection follows a systematic process leveraging the core components:

### 4.1 Process Flow

1. **Intent and Domain Inference**
   - LucaManager analyzes user query and stores it in ContextStore
   - Previous interactions in ContextStore provide additional context
   - Domain is identified (general, web, data science, quantitative finance)

2. **Capability Requirements**
   - Task is broken down into required capabilities
   - ToolRegistry is consulted to map capabilities to tools
   - Gap analysis identifies missing capabilities

3. **Specialist Assignment**
   - Specialists are selected based on required capabilities
   - Selection is optimized to minimize the number of agents
   - Specialist availability and performance is considered

4. **Execution and Monitoring**
   - Specialists execute tasks using approved tools
   - Progress is monitored and recorded in ContextStore
   - Errors are captured and handled according to Error-Payload Schema

5. **Result Integration**
   - Results from multiple specialists are integrated
   - Conflicts are resolved based on priority rules
   - Final outcome is validated before presentation

### 4.2 Adaptation Engine and Metrics

The system collects and uses performance metrics to improve future agent selection:

```python
class MetricRecord(BaseModel):
    """Performance metrics for a completed task or agent execution."""
    task_id: str
    agent_id: Optional[str] = None
    timestamp: datetime = Field(default_factory=datetime.utcnow)
    latency_ms: int
    error_count: int
    user_feedback_score: Optional[float] = None
    tokens_used: int
    completion_status: Literal["success", "partial", "failure"]
    domain: str
    learning_mode: str
    additional_metrics: Dict[str, Any] = {}
```

These metrics are stored in ContextStore and used by the Adaptation Engine to adjust weightings for agent selection over time, implementing a simple bandit algorithm for optimization.

## 5. Agent Configuration Structure

### 5.1 Base Configuration

```yaml
# Core component configuration
components:
  context_store:
    type: "sqlite"
    path: "./data/context.db"
    backup_interval: 300  # seconds
    
  tool_registry:
    default_scope: "/workspace/luca/**"
    version_check: true
    
  error_schema:
    levels: ["info", "warning", "error", "critical"]
    telemetry_enabled: true

# Base agent configuration
agents:
  luca:
    name: "Luca"
    role: "Manager"
    description: "Main orchestration agent that coordinates all tasks"
    model: "gpt-4o"
    temperature: 0.2
    system_prompt: "You are Luca, the AutoGen development assistant..."
    max_retries: 3
    timeout_seconds: 300
```

### 5.2 Specialist Configuration

```yaml
# Specialist agent configuration
specialists:
  coder:
    name: "Coder"
    role: "Developer"
    description: "Specialist agent for writing and refactoring code"
    model: "gpt-4"
    temperature: 0.1
    system_prompt: "You are a coding specialist..."
    capabilities:
      - "code_generation"
      - "code_review"
      - "refactoring"
    tools:
      - "file_io.read_text"
      - "file_io.write_text"
      - "git_tools.get_git_diff"
    sandbox:
      allowed_paths: ["/workspace/luca/**"]
      execution_timeout: 60  # seconds
```

### 5.3 Domain-Specific Configuration

```yaml
# Domain-specific configurations
domains:
  general:
    description: "General-purpose development"
    active_specialists:
      - "coder"
      - "tester"
      - "doc_writer"
    
  quantconnect:
    description: "QuantConnect development"
    active_specialists:
      - "coder"
      - "tester"
      - "analyst"
    specialist_settings:
      coder:
        system_prompt: "You are a coding specialist focusing on QuantConnect algorithms..."
      analyst:
        model: "gpt-4o"
```

### 5.4 Error Handling Configuration

```yaml
# Error handling configuration
error_handling:
  default:
    max_retries: 3
    backoff_factor: 1.5
    retry_statuses: ["timeout", "temporary_failure"]
    
  critical:
    escalation_path: "user_notification"
    recovery_strategies:
      - "restart_agent"
      - "switch_model"
      - "human_intervention"
```

## 6. Project Management Architecture

The system maintains a structured project framework that persists across sessions:

```python
class Project(BaseModel):
    """Project representation for persistent state across sessions."""
    id: str
    name: str
    description: str
    domain: str  # References domain preset
    created_at: datetime
    updated_at: datetime
    git_repository: Optional[str] = None
    conversations: List[str] = []  # References to conversation IDs
    files: Dict[str, str] = {}  # filename -> file content hash
    custom_agents: List[str] = []  # References to custom agent IDs
```

Projects are persisted in ContextStore and exposed through:

1. **UI Project Browser** - Grid or list view in sidebar
2. **Conversation References** - Each chat session links to its parent project
3. **File Management** - Projects track associated files and their state

The Project entity serves as a coordination point for all agents, establishing context and boundaries for operations.

### 6.1 Ticket Export Functionality

Project includes a ticket export capability for audit and compliance:

```python
def export_ticket(self) -> str:
    """Serializes conversation, files changed, and metrics into a JSON bundle for auditors."""
    # Collects all relevant data from ContextStore
    # Formats it according to the ticket schema
    # Returns a serialized JSON string or path to the exported file
```

This function enables users to export a complete record of their interaction with LUCA, including all conversations, file changes, and performance metrics. The exported ticket can be used for audit purposes, team collaboration, or compliance requirements.

## 7. Sandbox Architecture

### 7.1 Sandbox Implementation

LucaManager chooses per-task DockerSandbox until Phase 2 metrics prove a need for per-agent persistence. This approach ensures clean, isolated execution environments for each task without introducing unnecessary complexity.

```python
class SecurityManager:
    def create_sandbox(self, security_level: str) -> Sandbox:
        """Create an appropriate sandbox based on security level."""
        if security_level == "high":
            return DockerSandbox(
                image="python:3.13-slim",
                memory_limit="2g",
                cpu_limit=2.0,
                network="none",
                read_only_paths=["/lib", "/bin", "/usr"],
                writable_paths=["/workspace"],
                timeout_seconds=60
            )
        elif security_level == "medium":
            return SubprocessSandbox(
                cwd="/workspace",
                timeout_seconds=30,
                env={"PYTHONPATH": "/workspace"}
            )
        else:
            return LocalSandbox(
                cwd="/workspace",
                timeout_seconds=15
            )
```

### 7.2 Sandbox Selection Criteria

Phase 0 prioritizes security and isolation with DockerSandbox for all tasks. In Phase 2, based on performance metrics, the system may selectively use:

- DockerSandbox (high security) - For file operations and code execution
- SubprocessSandbox (medium security) - For lightweight operations with known tools
- LocalSandbox (low security) - For read-only operations in trusted contexts

## 8. UI Integration

The UI integration builds on top of the core components:

### 8.1 Chat Interface

1. **Message Processing**
   - User messages captured and stored in ContextStore
   - LucaManager processes messages through core loop
   - Responses formatted based on learning mode and preferences

2. **Status Visualization**
   - Real-time display of active agents and their status
   - Progress indicators for long-running tasks
   - Error notifications with appropriate context

3. **Context Awareness**
   - UI displays relevant context from ContextStore
   - Previous interactions are accessible and searchable
   - Project state is visible and navigable

### 8.2 Configuration Interface

1. **Agent Management**
   - Configure specialist parameters and models
   - View agent metrics and performance
   - Enable/disable specialists based on needs

2. **Tool Management**
   - View available tools from ToolRegistry
   - Configure tool parameters and permissions
   - Monitor tool usage and performance

3. **Domain and Mode Selection**
   - Switch between domain presets
   - Select learning mode (Noob, Pro, Guru)
   - Customize domain-specific settings

## 9. MCP Integration Architecture

### 9.1 MCP Server Structure

MCP servers provide standardized interfaces for various capabilities:

```python
@server.tool()
async def read_file(path: str) -> str:
    """Read a file from the filesystem."""
    try:
        with open(path, 'r', encoding='utf-8') as f:
            return f.read()
    except Exception as e:
        return f"Error: {str(e)}"
```

### 9.2 Server Availability by Domain

- Filesystem, ChromaDB, LightRAG, Graffiti auto-start for any domain
- QuantConnect server auto-starts **only** for `quantitative_finance` domain
- New servers declare `allowed_domains` during registration
- Security boundaries enforced at server connection time

### 9.3 MCP-AutoGen Bridge

```python
class MCPAutogenBridge:
    def get_autogen_tools(self) -> List[FunctionTool]:
        """Convert MCP tools to AutoGen function tools."""
        
    def execute_mcp_tool(self, tool_name: str, arguments: Dict[str, Any]) -> Any:
        """Execute an MCP tool and return the result."""
```

## 10. Conclusion

This architecture emphasizes building a solid foundation with the four core skeleton components before adding advanced features. By focusing on the ContextStore, ToolRegistry, Error-Payload Schema, and LucaManager, we create a robust system capable of handling complex agent orchestration.

The phased implementation approach ensures that each layer is thoroughly tested before moving to the next, reducing risks and ensuring a stable product. The agent hierarchy builds naturally on top of this foundation, leveraging the primitives to create an intelligent, adaptive system.

Every component serves a specific purpose, with clear rationales for its inclusion and placement within the implementation phases. This clarity will guide development decisions and ensure that the architecture remains coherent as LUCA evolves.

---

*Created by Claude on 2025-05-12 for LUCA Dev Assistant project*