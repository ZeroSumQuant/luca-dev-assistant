# AutoGen CI Mock Interference Research

## Problem Statement

Registry execute tests return MagicMock objects in CI but execute real functions locally, despite the ToolRegistry component being isolated from AutoGen.

## Context

PR #75 and #76 revealed a critical issue where setting `AUTOGEN_USE_MOCK_RESPONSE=1` in CI causes function execution to be replaced with MagicMock objects throughout the codebase, even in components that don't directly use AutoGen.

## Findings

### Root Cause Analysis

**MagicMock Injection in CI**: The unexpected MagicMock return stems from AutoGen's test-mode monkeypatching. In GitHub Actions, the environment variable `AUTOGEN_USE_MOCK_RESPONSE=1` triggers AutoGen's internal logic to globally replace certain function calls with mocks.

AutoGen's framework uses broad monkeypatches (via `unittest.mock.MagicMock`) to avoid real executions when running in CI. The ToolRegistry.execute_tool method isn't directly part of AutoGen, but its target function is being monkeypatched by AutoGen's test harness. Essentially, the registry looks up a tool function in `globals()`/`sys.modules`, but by the time it runs in CI, that function object has been replaced by a MagicMock.

**Call Stack and Injecting Module**: The injection appears to come from the AutoGen extension (autogen-ext) or core libraries at runtime – likely in the code execution or model response handling modules. The maintainers noted that "the mock approach is for all clients rather than an instance", meaning the entire system is patched when test mode is on.

Key points:
- AutoGen components (possibly `OpenAIChatCompletionClient` or a code executor in `autogen_ext`) are wrapping or replacing tool calls with MagicMock objects in CI
- This behavior does not occur locally due to subtle environment differences (OS and test context)
- On macOS, AutoGen might fall back to local execution, whereas on Ubuntu CI the conditions trigger full mocking
- The presence of both `pyautogen==0.9.0` (AG2 fork) and `autogen-agentchat==0.5.6` might introduce unpredictable behavior

### Design Intent

**Purpose of `AUTOGEN_USE_MOCK_RESPONSE`**: This environment variable is intended as a master switch to enable offline testing mode. The AutoGen framework introduced it to avoid calling real external APIs (like OpenAI or other LLM services) during tests and CI runs.

Design goals:
- Improve test reliability and speed
- Avoid calling real LLMs in unit tests for development velocity
- Return consistent fake data to any request that would normally reach out to an LLM

**Intended Scope of Mocking**: 
- Mainly aimed at model clients (LLM calls)
- Should stop at the point where the AI model would normally produce output
- Tool registry functions are internal Python functions – not external API calls – so they were likely not intended to be replaced wholesale by MagicMocks

**Where Mocking Begins and Ends**:
- Mocking starts at the Agent/Model interface
- May extend to code execution tools (especially Docker-based executors)
- Currently applies mocks too broadly, affecting tool calls inside agent workflows
- Ideally should mock only LLM API responses and dangerous tool actions, not pure in-memory function logic

### System Behavior Differences (CI vs Local)

**AutoGen's CI Mode**:
- Combination of `CI=true` and `AUTOGEN_USE_MOCK_RESPONSE=1` creates different runtime behavior
- GitHub Actions always sets `CI=true` by default
- In this mode, LLM calls are intercepted and tool execution may be altered

**Import-Time vs Dynamic Patching**:
- Injection likely occurs dynamically at runtime
- During agent setup, tools might be wrapped in proxies that return MagicMocks under certain conditions
- OS differences (Docker availability on Linux vs Mac) can trigger alternate code paths

**Conditional Mocking**:
- Mocking is conditional on environment variables
- MagicMock could be applied "late" when an agent is about to perform a tool action
- In CI, patches might apply at session start, whereas locally the conditions for activation weren't fully met

### Testing Strategy Implications

**Real vs Mocked Execution**: The discrepancy raises questions about how tests should handle tool execution:

1. **If real functions should run in tests**: Mocking should be selectively disabled for those tests
2. **If CI should enforce mock-based tests**: Registry tests could be adapted to expect MagicMocks (though this seems insufficient)

**Recommended Strategy**:
- Use selective environment override with pytest's monkeypatch
- Tag tests that require real execution with markers
- Follow AutoGen's example of recording and replaying interactions
- Ensure monkeypatches are properly reverted

**Preventing Leaks**: Use pytest's monkeypatch fixture and mocker to auto-undo patches after tests.

## Recommendations

### Short-term Fix

The cleanest immediate fix is to override the problematic environment setting in the context of ToolRegistry tests:

```python
import os
os.environ["AUTOGEN_USE_MOCK_RESPONSE"] = "0"
```

Or use a pytest fixture:

```python
@pytest.fixture(autouse=True)
def disable_autogen_mock(monkeypatch):
    monkeypatch.setenv("AUTOGEN_USE_MOCK_RESPONSE", "0")
```

### Long-term Safeguards

1. **Isolate Third-Party Effects**: 
   - Add boundaries or abstractions around tool execution
   - Design explicit interfaces for tool invocation instead of relying on global lookups

2. **Prevent Global Monkeypatching**:
   - Work with AutoGen community to narrow the broad mocking
   - Encapsulate tools to shield them from AutoGen's mock

3. **Test Hygiene**:
   - Clear or reset modified global state after tests
   - Use dedicated test sessions with different mock settings
   - Consider multiple CI pipelines for unit vs integration tests

4. **Protect Isolated Components**:
   - Document that ToolRegistry should be tested with AutoGen's mocking disabled
   - Ensure minimal coupling between components

5. **Future-Proofing**:
   - Monitor AutoGen updates for better test utilities
   - Consider removing env var usage in favor of explicit mocks

## Implementation Notes

1. Add an assertion in registry tests to detect unexpected mocks:
   ```python
   func = registry._resolve_tool("my_tool")
   assert not isinstance(func, unittest.mock.MagicMock), "Tool function was mocked unexpectedly"
   ```

2. Document testing philosophy in CONTRIBUTING.md explaining mock behavior

3. Consider removing `pyautogen` dependency if not needed (it's the AG2 fork, not official)

4. Add logging warnings in ToolRegistry when MagicMocks are detected

## References

- PR #75: Initial module import errors
- PR #76: Fix attempt revealing mock interference
- GitHub Actions default environment variables (CI=true)
- AutoGen maintainers on challenges of MagicMock-based testing
- AutoGen migration guide noting pyautogen vs autogen-agentchat (fork vs official)

## Test Verification

```python
# Fixture to disable AutoGen mocking for specific tests
@pytest.fixture
def real_execution(monkeypatch):
    """Temporarily disable AutoGen's mock mode for tests that need real execution."""
    monkeypatch.setenv("AUTOGEN_USE_MOCK_RESPONSE", "0")
    yield
    # Cleanup happens automatically with monkeypatch

# Usage in tests
def test_execute_tool_real_behavior(real_execution):
    """Test with real function execution, not mocks."""
    result = registry.execute_tool("example_tool", {"message": "test"})
    assert result == "test x 1"  # Expect real result, not MagicMock
```