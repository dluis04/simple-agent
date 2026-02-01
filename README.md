# Simple Conversational Agent

A basic instruction-following agent demonstrating the fundamental agent loop: **Observe → Think → Act**

## Features

- **Conversational Interface**: Natural language interaction with Claude
- **Action Execution**: Built-in tools for calculations, memory storage, and search
- **Agent Loop**: Clear implementation of observe-think-act pattern
- **Two Implementations**: Manual parsing (learning) and native tool use (production)

## Quick Start

```bash
# 1. Install dependencies
uv sync

# 2. Configure API key
cp .env.example .env
# Edit .env: ANTHROPIC_API_KEY=sk-ant-xxxxx

# 3. Run the agent
uv run simple-agent
```

## Project Structure

```
simple-agent/
├── src/simple_agent/        # Main package
│   ├── __init__.py          # Public exports
│   ├── base.py              # BaseAgent class
│   ├── simple.py            # SimpleAgent (manual parsing)
│   ├── advanced.py          # AdvancedAgent (native tool use)
│   └── tools.py             # Shared tools
├── examples/
│   └── demo.py              # Usage examples
├── scripts/
│   └── verify_setup.py      # Setup verification
├── tests/                   # Test files
├── pyproject.toml
└── README.md
```

## Usage

### Command Line

```bash
uv run simple-agent      # Run simple agent
uv run advanced-agent    # Run advanced agent
```

### Programmatic

```python
from simple_agent import SimpleAgent, AdvancedAgent

agent = SimpleAgent()
response, results = agent.run_step("Calculate 25 * 4")
print(response)
```

## How It Works

### The Agent Loop

```
┌─────────────────────────────────────────────────────────────┐
│  ┌──────────────┐      ┌──────────────┐     ┌────────────┐  │
│  │   OBSERVE    │─────▶│    THINK     │────▶│    ACT     │  │
│  │ Get input    │      │ Query LLM    │     │ Parse &    │  │
│  │ Store history│      │ With context │     │ Execute    │  │
│  └──────────────┘      └──────────────┘     └────────────┘  │
│         ▲                                          │        │
│         └──────────────────────────────────────────┘        │
└─────────────────────────────────────────────────────────────┘
```

## Available Tools

| Tool | Description | Example |
|------|-------------|---------|
| `calculate` | Math expressions | `25 * 4` or `2^10` |
| `save_note` | Store information | `Meeting at 3pm` |
| `search_memory` | Find saved notes | `meeting` |

## Two Implementations

### SimpleAgent (Manual Parsing)

Uses pattern matching to extract `ACTION: tool: param` from LLM output.

**Best for**: Learning, full control, simple use cases

### AdvancedAgent (Native Tool Use)

Uses Anthropic's built-in tool feature with structured schemas.

**Best for**: Production, reliability, complex workflows

## Extending

### Add a New Tool

```python
# In src/simple_agent/tools.py
def my_tool(self, param: str) -> dict:
    return {"result": param.upper()}

# Add to TOOL_SCHEMAS for AdvancedAgent
```

### Create a Custom Agent

```python
from simple_agent import SimpleAgent

class MyAgent(SimpleAgent):
    def get_system_prompt(self):
        return "Custom prompt..."
```

## Resources

- [Anthropic Documentation](https://docs.anthropic.com/)
- [Tool Use Guide](https://docs.anthropic.com/en/docs/build-with-claude/tool-use)
- [TUTORIAL.md](TUTORIAL.md) - Step-by-step learning guide

## License

MIT License
