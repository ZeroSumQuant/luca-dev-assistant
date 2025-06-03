# Module Import Shadow Issue: Deep Dive Analysis

**Date**: 2025-05-18
**Author**: Claude & ZeroSumQuant
**Tags**: Python, pytest, CI/CD, module-imports, test-discovery

## Executive Summary

A critical CI failure was caused by pytest's test discovery mechanism creating a shadow package that prevented submodule imports. The issue manifested as `ModuleNotFoundError` for `luca_core` submodules, despite the parent module importing successfully. The root cause was a naming collision between `tests/luca_core/` and the actual `luca_core` package.

## The Problem

### Symptoms

1. **CI Failures**: 225 tests passed, but all `luca_core` submodule imports failed
2. **Error Pattern**: `ModuleNotFoundError: No module named 'luca_core.schemas'`
3. **Inconsistency**: Parent module `luca_core` imported fine, but submodules failed
4. **Registry Tests**: Additional failures due to AutoGen mocking interference

### Initial Confusion

- Adding `PYTHONPATH` didn't help
- `pip install -e .` was already in place
- Local tests passed, CI tests failed
- Module was clearly installed but submodules were "missing"

## Root Cause Analysis

### Python Import Mechanics

When pytest starts, it modifies `sys.path` to include test directories:

```python
# sys.path during pytest execution
[
    '',                    # Current directory
    'tests',               # Added by pytest
    'tests/luca_core',     # Problem: shadows real package!
    '/path/to/site-packages',  # Where real luca_core lives
]
```

### The Shadow Effect

1. Python finds `tests/luca_core/` before the real `luca_core` package
2. `import luca_core` succeeds (loads `tests/luca_core/__init__.py`)
3. `import luca_core.schemas` fails (no `schemas` in test directory)
4. The test directory acts as an empty namespace package

### Why It Worked Locally

- Different pytest configurations
- Virtual environment setups
- IDE running tests differently than CI

## The Fix

### Step 1: Rename Test Directory

```bash
git mv tests/luca_core tests/luca_core_pkgtests
```

This eliminates the naming collision entirely.

### Step 2: Handle AutoGen Mocking

Registry tests were failing due to AutoGen's global mocking:

```python
# Mark tests requiring real execution
pytestmark = pytest.mark.real_exec
```

### Step 3: Update CI Workflow

Separate test runs for different environments:

```yaml
# Mocked tests
- run: pytest tests/tools tests/test_mcp_integration.py
  env:
    AUTOGEN_USE_MOCK_RESPONSE: "1"

# Real execution tests
- run: pytest tests/core/test_registry_execute.py
  env:
    AUTOGEN_USE_MOCK_RESPONSE: "0"

# All other tests
- run: pytest --ignore=tests/tools --ignore=tests/test_mcp_integration.py --ignore=tests/core/test_registry_execute.py
```

### Step 4: Docker Configuration

Skip real_exec tests in Docker where mocking is enabled:

```dockerfile
CMD ["pytest", "-q", "-m", "not real_exec"]
```

## Lessons Learned

### 1. Test Directory Naming

**Never** name test directories the same as packages they test:
- ❌ `tests/luca_core/` (shadows `luca_core` package)
- ✅ `tests/luca_core_tests/` or `tests/luca_core_pkgtests/`

### 2. Import Debugging

Diagnostic commands that helped:

```python
# Check import paths
import luca_core
print(luca_core.__file__)
print(luca_core.__path__)

# Verify sys.path order
import sys
for i, p in enumerate(sys.path):
    print(f"[{i}] {p}")
```

### 3. CI/CD Environment Differences

Always consider:
- Environment variable differences (`CI=true`)
- Mock framework behavior (AutoGen's `AUTOGEN_USE_MOCK_RESPONSE`)
- Test discovery mechanisms
- Path resolution differences

### 4. Shadow Package Detection

Warning signs of shadow packages:
- Parent imports work, submodules fail
- `__path__` attribute missing or wrong
- Import location not in site-packages
- Inconsistent behavior between environments

## Prevention Strategies

### 1. Naming Conventions

```
project/
├── src/
│   └── package_name/
└── tests/
    └── package_name_tests/  # Note the suffix
```

### 2. Import Guards

```python
# In tests, verify correct import
import luca_core
assert 'site-packages' in luca_core.__file__, "Importing shadow package!"
```

### 3. CI Configuration

- Test imports explicitly in CI
- Log `sys.path` and module locations
- Run diagnostic scripts before tests

## Timeline of Discovery

1. **Initial Failure**: Import errors in CI, tests pass locally
2. **Wrong Paths**:
   - Tried `PYTHONPATH` manipulation
   - Updated `setup.py` with package_dir
   - Modified `pytest.ini` settings
3. **Deep Diagnostics**:
   - Discovered `tests/luca_core` in sys.path
   - Found shadow package behavior
   - Identified pytest's test discovery as culprit
4. **Solution**: Renamed directory, problem solved instantly

## Impact

- **Before**: 5+ hours debugging, multiple failed CI runs
- **After**: Immediate fix, all tests passing
- **Prevented**: Future developers hitting same issue

## References

- [pytest test discovery](https://docs.pytest.org/en/stable/explanation/pythonpath.html)
- [Python import system](https://docs.python.org/3/reference/import.html)
- [PEP 420: Namespace Packages](https://www.python.org/dev/peps/pep-0420/)

## Conclusion

What appeared to be a complex module installation issue was actually a simple naming collision. The lesson: when debugging import issues, always check for shadow packages created by test discovery mechanisms. The fix was a one-line directory rename, but the debugging journey provided valuable insights into Python's import machinery and pytest's behavior.