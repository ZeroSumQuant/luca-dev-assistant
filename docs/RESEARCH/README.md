# LUCA Research Documentation

This directory contains research findings, deep investigations, and architectural insights discovered during LUCA development.

## Naming Conventions

Research documents should follow this naming pattern:
```
YYYY-MM-DD-type-brief-description.md
```

Where:
- `YYYY-MM-DD`: Date the research was conducted
- `type`: One of:
  - `autogen` - AutoGen specific behavior
  - `arch` - Architecture patterns and designs
  - `bug` - Deep investigations into bugs
  - `perf` - Performance analysis
  - `pattern` - Design patterns or best practices
  - `integration` - Integration issues with external tools
- `brief-description`: A short, hyphenated description (3-5 words)

## Categories

### /autogen-mocking
Research related to AutoGen's mocking behavior and how it affects our components.

### /architecture
Architectural patterns, safeguards, and design decisions.

### /performance
Performance investigations, benchmarks, and optimization research.

### /bugs
Deep investigations into complex bugs requiring extensive research.

## Research Template

Each research document should include:

1. **Problem Statement**: Clear description of what we're investigating
2. **Context**: Relevant background and why this research is needed
3. **Findings**: What we discovered
4. **Recommendations**: Proposed solutions or actions
5. **Implementation Notes**: How to apply the findings
6. **References**: Links to documentation, issues, or external resources

## Current Research Topics

1. AutoGen Mocking Interference (2025-05-18) - How AutoGen's test mocking affects isolated components
2. Module Import Shadows (2025-05-18) - Critical discovery: pytest test discovery can create shadow packages when test directories match package names
3. [Add future topics as they're researched]

## Notable Findings

### Module Import Shadow Issue
**Critical**: Never name test directories the same as package names. For example, `tests/luca_core/` will shadow the real `luca_core` package and prevent submodule imports. This is documented in detail at:
- Research doc: `/module-import-ci-failures/2025-05-18-module-import-shadows.md`
- Contributing guide: `CONTRIBUTING.md` section on test directory naming
- Handoff docs: `/docs/handoff/2025-05-18-2.md`