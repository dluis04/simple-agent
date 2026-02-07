# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Development Commands

```bash
# Install dependencies
uv sync

# Run all tests
uv run pytest tests/ -v

# Run a single test file
uv run pytest tests/test_tools.py -v

# Run a specific test
uv run pytest tests/test_tools.py::test_calculate_basic -v

# Format and lint
pre-commit run --all-files

# Before creating PR
pre-commit run --all-files && uv run pytest tests/ -v

# Run the agents
uv run simple-agent       # Interactive SimpleAgent
uv run advanced-agent     # Interactive AdvancedAgent
```

## Architecture

This project implements the **Observe-Think-Act** pattern for conversational AI agents.

### Core Components

**Base Agent** (`src/simple_agent/base.py`): Abstract base class that manages:
- Anthropic client initialization and API calls
- Conversation history with sliding window trimming (`max_history_length=50`)
- Interactive REPL loop
- Shared `ToolRegistry` instance

**Two Agent Implementations:**
- **SimpleAgent** (`simple.py`): Parses `ACTION: tool_name: parameter` from LLM text output using regex. Educational/prototype use.
- **AdvancedAgent** (`advanced.py`): Uses Anthropic's native tool use API with JSON schemas. Production use.

**ToolRegistry** (`tools.py`): Provides shared tools:
- `calculate()` - Safe math evaluation using AST (prevents code injection)
- `save_note()` / `search_memory()` - Session-based memory

### Control Flow

```
User Input → run_step() → OBSERVE (add to history) → THINK (Claude API) → ACT (parse/execute tools) → Response
```

For Advanced Agent, the ACT phase loops on `stop_reason == "tool_use"` until `"end_turn"`.

### Adding Tools

1. Add method to `ToolRegistry` in `tools.py`
2. For AdvancedAgent: add schema to `TOOL_SCHEMAS` list
3. For SimpleAgent: add case in `execute_action()` method
