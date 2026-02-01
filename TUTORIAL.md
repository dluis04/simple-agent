# Building a Conversational Agent - Tutorial

This tutorial walks through building a conversational agent step by step. For setup instructions and project overview, see [README.md](README.md).

## Table of Contents

1. [Making Your First API Call](#1-making-your-first-api-call)
2. [Building the Agent Loop](#2-building-the-agent-loop)
3. [Prompt Engineering for Agents](#3-prompt-engineering-for-agents)
4. [Parsing LLM Output](#4-parsing-llm-output)
5. [Implementing Tools](#5-implementing-tools)
6. [Native Tool Use](#6-native-tool-use)

---

## 1. Making Your First API Call

```python
from anthropic import Anthropic
import os

client = Anthropic(api_key=os.getenv("ANTHROPIC_API_KEY"))

response = client.messages.create(
    model="claude-3-5-sonnet-20250122",
    max_tokens=1024,
    messages=[{"role": "user", "content": "Hello, Claude!"}]
)

print(response.content[0].text)
```

---

## 2. Building the Agent Loop

### Step 1: OBSERVE

```python
def observe(self):
    """Get input from user."""
    user_input = input("You: ").strip()
    return user_input
```

### Step 2: THINK

```python
def think(self, user_input):
    """Send input to LLM and get response."""
    self.conversation_history.append({
        "role": "user",
        "content": user_input
    })

    response = self.client.messages.create(
        model=self.model,
        max_tokens=1024,
        system=self.system_prompt,
        messages=self.conversation_history
    )

    response_text = response.content[0].text

    self.conversation_history.append({
        "role": "assistant",
        "content": response_text
    })

    return response_text
```

**Key Points:**
- Maintain conversation history for context
- Include system prompt for behavior guidance
- Append both user and assistant messages

### Step 3: ACT

```python
def act(self, response_text):
    """Parse response and execute any actions."""
    actions = self.parse_actions(response_text)

    results = []
    for action in actions:
        result = self.execute_action(action)
        results.append(result)

    return results
```

---

## 3. Prompt Engineering for Agents

The system prompt defines agent behavior. Key elements:

```python
system_prompt = """You are a helpful AI assistant.

You can perform the following actions:
- calculate: Perform math (ACTION: calculate: 5+3)
- save_note: Save information (ACTION: save_note: text)
- search_memory: Find saved notes (ACTION: search_memory: query)

When you want to take an action, use this format:
ACTION: action_name: parameter

Be helpful and concise."""
```

### Best Practices

1. **Be Specific**: Clearly define expected behaviors
2. **Provide Examples**: Show the exact format you want
3. **Define Boundaries**: Explain what the agent can/cannot do
4. **Iterate**: Test and refine based on actual behavior

### Common Patterns

**Chain of Thought:**
```python
system_prompt = """Before answering, think step by step.
Show your reasoning process."""
```

**Structured Output:**
```python
system_prompt = """Format your responses as:
REASONING: [Your thought process]
ACTION: [Any tools to use]
RESPONSE: [Your answer to the user]"""
```

---

## 4. Parsing LLM Output

### Pattern Matching (Simple)

```python
def parse_actions(self, response_text):
    """Extract actions using string matching."""
    actions = []

    for line in response_text.split('\n'):
        if line.strip().startswith('ACTION:'):
            action_part = line[7:].strip()  # Remove "ACTION:"

            if ':' in action_part:
                tool, param = action_part.split(':', 1)
                actions.append({
                    'tool': tool.strip(),
                    'parameter': param.strip()
                })

    return actions
```

**Example:**
```
Input: "Let me calculate that.\nACTION: calculate: 5 + 3\nThe result is 8."
Output: [{'tool': 'calculate', 'parameter': '5 + 3'}]
```

### JSON Parsing

```python
system_prompt = """When you want to use a tool, output JSON:
{"action": "tool_name", "parameters": {"param1": "value1"}}"""

def parse_actions(self, response_text):
    import json
    import re

    json_pattern = r'\{.*?\}'
    matches = re.findall(json_pattern, response_text, re.DOTALL)

    actions = []
    for match in matches:
        try:
            action = json.loads(match)
            if 'action' in action:
                actions.append(action)
        except json.JSONDecodeError:
            continue

    return actions
```

---

## 5. Implementing Tools

### Tool Design

```python
def calculate(self, expression):
    """Perform mathematical calculation."""
    try:
        # Safety: only allow math characters
        if not re.match(r'^[\d\s+\-*/().]+$', expression):
            return "Error: Invalid expression"

        result = eval(expression)
        return f"Result: {result}"
    except Exception as e:
        return f"Error: {str(e)}"
```

### Tool Registry

```python
class Agent:
    def __init__(self):
        self.memory = []
        self.tools = {
            "calculate": self.calculate,
            "save_note": self.save_note,
            "search_memory": self.search_memory
        }

    def execute_action(self, tool_name, parameter):
        if tool_name in self.tools:
            return self.tools[tool_name](parameter)
        return f"Error: Unknown tool '{tool_name}'"

    def save_note(self, note):
        self.memory.append(note)
        return f"Saved: {note}"

    def search_memory(self, query):
        results = [n for n in self.memory if query.lower() in n.lower()]
        if results:
            return "Found:\n" + "\n".join(f"- {r}" for r in results)
        return "No matches found"
```

### Tool Design Principles

1. **Single Responsibility**: Each tool does one thing well
2. **Clear Interface**: Obvious parameters and return values
3. **Error Handling**: Return useful error messages
4. **Safety**: Validate inputs, prevent harmful operations

---

## 6. Native Tool Use

Anthropic's API provides built-in tool support for better reliability.

### Define Tool Schema

```python
tools = [{
    "name": "calculate",
    "description": "Perform a mathematical calculation",
    "input_schema": {
        "type": "object",
        "properties": {
            "expression": {
                "type": "string",
                "description": "Math expression to evaluate"
            }
        },
        "required": ["expression"]
    }
}]
```

### Tool Use Loop

```python
def run_with_tools(self, user_input):
    messages = [{"role": "user", "content": user_input}]

    while True:
        response = self.client.messages.create(
            model=self.model,
            max_tokens=1024,
            tools=self.tools,
            messages=messages
        )

        if response.stop_reason == "end_turn":
            return response.content[0].text

        elif response.stop_reason == "tool_use":
            messages.append({
                "role": "assistant",
                "content": response.content
            })

            tool_results = []
            for block in response.content:
                if block.type == "tool_use":
                    result = self.execute_tool(block.name, block.input)
                    tool_results.append({
                        "type": "tool_result",
                        "tool_use_id": block.id,
                        "content": str(result)
                    })

            messages.append({"role": "user", "content": tool_results})
```

### Benefits of Native Tool Use

- No manual parsing needed
- Automatic validation
- More reliable
- Better multi-tool handling

---

## Practice Exercises

1. Add a temperature conversion tool
2. Implement a "history" command to show conversation
3. Add a web search tool using an API
4. Create a multi-agent system with specialized agents

## Resources

- [Anthropic API Documentation](https://docs.anthropic.com/)
- [Tool Use Guide](https://docs.anthropic.com/en/docs/build-with-claude/tool-use)
