# LUCA Research Quick Reference

## Critical Issues & Solutions

### 1. Module Import Failures (`ModuleNotFoundError`)
**Problem**: Parent module imports but submodules fail
**Likely Cause**: Shadow package from test directory
**Solution**: Check for test directories matching package names
**Fix**: Rename `tests/package_name/` → `tests/package_name_tests/`
**Details**: `/module-import-ci-failures/2025-05-18-module-import-shadows.md`

### 2. AutoGen Mock Interference
**Problem**: Tests fail when AutoGen mocking is enabled globally
**Solution**: Use `pytest.mark.real_exec` marker and separate CI runs
**Details**: `/autogen-mocking/2025-05-18-autogen-ci-mock-interference.md`

### 3. CI Test Failures (but local tests pass)
**Check**:
1. Environment differences (AUTOGEN_USE_MOCK_RESPONSE)
2. Test directory naming collisions
3. pytest test discovery adding paths to sys.path
4. Mock vs real execution requirements

## Debugging Commands

```bash
# Check module import location
python -c "import luca_core; print(luca_core.__file__)"

# Check sys.path during pytest
pytest --collect-only -q tests/

# Verify test markers
pytest --markers | grep real_exec
```

## Key Documentation Locations

- **Research Documents**: `/RESEARCH/*/` 
- **Handoff Reports**: `/docs/handoff/YYYY-MM-DD-N.md`
- **Task Logs**: `/docs/task_log_YYYY_MM.md`
- **Contributing Guide**: `/CONTRIBUTING.md`
- **CLAUDE.md**: Project memory file

## Common Pitfalls

1. **Never** name test directories the same as packages
2. **Always** check if tests need real vs mocked execution
3. **Remember** AutoGen mocking is process-wide
4. **Consider** CI environment differences in debugging