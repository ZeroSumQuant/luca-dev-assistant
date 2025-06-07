# LUCA Issues - Chronological Dependency Order
**Date**: June 7, 2025  
**Purpose**: Reorder all open issues based on dependencies to ensure proper development sequence

---

## Overview

This document reorders all 29 open issues based on their dependencies and logical development flow. Issues are grouped into phases that must be completed sequentially to avoid rework and ensure smooth integration.

---

## Phase 1: Foundation & Infrastructure (Must Do First)

These issues create the base infrastructure that other features depend on:

### 1.1 Core Security & Sandboxing
**Why First**: Safety infrastructure is required before any agent execution

- **#26** - Implement sandboxing strategy for user-provided code *(HIGH)*
  - Required for: All agent execution, CAKE integration
  - Blocks: #60, #50, #120

- **#60** - PH2-2: Sandbox limits module (CPU/MEM/DISK) *(MEDIUM)*
  - Depends on: #26
  - Required for: Safe agent execution

- **#27** - Add input validation to functions processing external data *(MEDIUM)*
  - Required for: Security across all components

### 1.2 Configuration & Architecture
**Why Early**: Configuration system needed before implementing features

- **#56** - PH1-1: YAML configuration loader *(MEDIUM)*
  - Required for: All configurable features
  - Blocks: #58, #57

- **#55** - CI-DEBT-#4: Type hygiene for store.py *(LOW)*
  - Required for: Clean type system before new features

- **#54** - CI-DEBT-#3: Fix legacy async tests *(LOW)*
  - Required for: Reliable test suite

---

## Phase 2: Core Agent System

These establish the agent framework that CAKE will wrap around:

### 2.1 Agent Infrastructure
- **#50** - PH2-1: SecurityAgent stub *(HIGH)*
  - Depends on: #26 (sandboxing)
  - Required for: Agent permission system

- **#51** - PH2-2: Analyst → QuantAnalyst rename *(LOW)*
  - Best done before: UI work to avoid double changes

### 2.2 Testing Fixes
**Why Now**: Fix tests before adding new features

- **#82** - Fix Streamlit UI and Resource Errors in Agent Manager Tests *(HIGH)*
  - Blocks: UI development

- **#83** - Fix Import Errors in app/**main**.py Coverage Tests *(MEDIUM)*

- **#84** - Fix Core Module Test Coverage and Mock Configuration *(MEDIUM)*

---

## Phase 3: Service Layer & Error Handling

These create the infrastructure for CAKE integration:

- **#30** - Implement service layer between UI and core *(MEDIUM)*
  - Required for: Clean CAKE integration point
  - Blocks: #29, #120

- **#96** - Add JSON Schema validation for documentation *(HIGH)*
  - Independent: Can be done anytime
  - Moved from Phase 8: Prevents documentation drift early

- **#29** - Implement robust error handling strategy in UI *(MEDIUM)*
  - Depends on: #30 (service layer)
  - Synergizes with: CAKE error handling

- **#59** - PH1-4: Improved logging and monitoring *(MEDIUM)*
  - Complements: CAKE monitoring

---

## Phase 4: CAKE Integration & Interrupt System

- **#120** - Time-traveling interrupt system *(HIGH)*
  - Depends on: #26, #30, #29
  - Implementation: Via CAKE integration
  - This is where CAKE gets integrated!
  - Note: CAKE is a monitoring layer, not an API

---

## Phase 5: Authentication & Session Management

- **#58** - PH1-3: Basic authentication and session management *(MEDIUM)*
  - Depends on: #56 (config loader)
  - Required for: Multi-user support

---

## Phase 6: UI Redesign & Enhancement

These can proceed after core infrastructure is stable:

- **#57** - PH1-2: Streamlit status panels *(MEDIUM)*
  - Depends on: #56 (config), #82 (UI tests fixed)
  - Perfect time to add: CAKE status indicators

- **#107** - UI Redesign: Main Chat Interface *(MEDIUM)*
  - Include: CAKE intervention display

- **#108** - UI Feature: Left Sidebar with Projects *(MEDIUM)*
  - Include: CAKE intervention history

- **#109** - UI Components: QuantConnect Results Display *(MEDIUM)*
  - Can be done in parallel with other UI work

- **#110** - Architecture: Domain-Specific UI Adaptability *(MEDIUM)*
  - Depends on: #107, #108 (basic UI complete)

---

## Phase 7: Tool Integration & Enhancement

- **#119** - Integrate Claude omniscience tools into LUCA *(MEDIUM)*
  - Best after: Core system stable
  - Enhances: Context understanding

- **#62** - PH2-4: Filesystem server location fix *(LOW)*
  - Can be done anytime after Phase 2

---

## Phase 8: Documentation & Quality

These can be done after main development:

- **#115** - Clean up root directory structure *(MEDIUM)*
  - Best as one of the last tasks

- **#63** - PH1-DOC: Docstring hygiene sweep *(LOW)*

- **#65** - PH1-DOC: Naming consistency & task log audit *(LOW)*

---

## Phase 9: Dependency Management (Can Do Anytime)

These are independent and can be done when convenient:

- **#31** - Modernize dependency management with Poetry *(LOW)*
  - Independent task

- **#32** - Improve Docker dependency management *(MEDIUM)*
  - Independent task

---

## Critical Path Summary

The critical path that blocks the most work:

1. **#26** (Sandboxing) → **#60** (Limits) → **#50** (SecurityAgent)
2. **#56** (Config) → **#58** (Auth) & **#57** (Status Panels)
3. **#30** (Service Layer) → **#29** (Error Handling) → **#120** (CAKE/Interrupts)
4. **#82** (UI Tests) → **#107-110** (UI Redesign)

---

## Recommended Work Order for Tonight

Based on dependencies and impact:

1. **Start with #26** - Sandboxing strategy (enables everything else)
2. **Then #56** - YAML config loader (many features need this)
3. **Fix #82** - UI test errors (blocks UI development)
4. **Do #30** - Service layer (clean integration point for CAKE)
5. **Do #96** - JSON Schema validation (independent, prevents drift)
6. **Do #29** - UI error handling (completes Phase 3)

Note: #120 (CAKE integration) comes later in Phase 4 after infrastructure is ready

---

## Notes

- Issues #31 and #32 (dependency management) can be done anytime without affecting other work
- Documentation issues (#63, #65, #96) are best done after features stabilize
- UI redesign (#107-110) should happen together as a cohesive effort
- CAKE integration naturally fits after security and service layer are established