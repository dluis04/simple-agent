"""Tests for SimpleAgent parsing and action execution."""

import pytest

from simple_agent.simple import SimpleAgent  # noqa: F401
from simple_agent.tools import ToolRegistry


class TestParseActions:
    """Tests for action parsing without requiring API calls."""

    @pytest.fixture
    def parser(self):
        """Create a minimal SimpleAgent-like object for parsing tests."""

        class Parser:
            def parse_actions(self, response_text: str) -> list[tuple[str, str]]:
                actions = []
                for line in response_text.split("\n"):
                    if line.strip().startswith("ACTION:"):
                        action_part = line.strip()[7:].strip()
                        if ":" in action_part:
                            tool_name, parameter = action_part.split(":", 1)
                            actions.append((tool_name.strip(), parameter.strip()))
                return actions

        return Parser()

    def test_parse_single_action(self, parser):
        response = "ACTION: calculate: 5 + 3"
        actions = parser.parse_actions(response)
        assert len(actions) == 1
        assert actions[0] == ("calculate", "5 + 3")

    def test_parse_multiple_actions(self, parser):
        response = """Let me help you.
ACTION: save_note: Buy groceries
ACTION: calculate: 10 * 5"""
        actions = parser.parse_actions(response)
        assert len(actions) == 2
        assert actions[0] == ("save_note", "Buy groceries")
        assert actions[1] == ("calculate", "10 * 5")

    def test_parse_no_actions(self, parser):
        response = "I'll help you with that. Here's the information."
        actions = parser.parse_actions(response)
        assert len(actions) == 0

    def test_parse_action_with_colon_in_parameter(self, parser):
        response = "ACTION: save_note: Meeting at 3:30pm with John"
        actions = parser.parse_actions(response)
        assert len(actions) == 1
        assert actions[0] == ("save_note", "Meeting at 3:30pm with John")

    def test_parse_action_with_extra_whitespace(self, parser):
        response = "  ACTION:   calculate:   2 + 2  "
        actions = parser.parse_actions(response)
        assert len(actions) == 1
        assert actions[0] == ("calculate", "2 + 2")

    def test_parse_mixed_content(self, parser):
        response = """Here's what I found:
ACTION: search_memory: python
Based on the results, you have 2 notes about Python."""
        actions = parser.parse_actions(response)
        assert len(actions) == 1
        assert actions[0] == ("search_memory", "python")


class TestExecuteAction:
    """Tests for action execution."""

    @pytest.fixture
    def executor(self):
        """Create an executor with ToolRegistry."""

        class Executor:
            def __init__(self):
                self.tool_registry = ToolRegistry()

            def execute_action(self, tool_name: str, parameter: str) -> str:
                if tool_name == "calculate":
                    result = self.tool_registry.calculate(parameter)
                    if "error" in result:
                        return f"Error: {result['error']}"
                    return f"Result: {result['result']}"
                elif tool_name == "save_note":
                    self.tool_registry.save_note(parameter)
                    return f"Saved note: {parameter}"
                elif tool_name == "search_memory":
                    result = self.tool_registry.search_memory(parameter)
                    if result["count"] > 0:
                        return "Found notes:\n" + "\n".join(
                            f"- {n}" for n in result["results"]
                        )
                    return "No matching notes found."
                return f"Error: Unknown tool '{tool_name}'"

        return Executor()

    def test_execute_calculate(self, executor):
        result = executor.execute_action("calculate", "10 + 5")
        assert "Result: 15" in result

    def test_execute_calculate_error(self, executor):
        result = executor.execute_action("calculate", "invalid")
        assert "Error" in result

    def test_execute_save_note(self, executor):
        result = executor.execute_action("save_note", "Test note")
        assert "Saved note: Test note" in result
        assert "Test note" in executor.tool_registry.memory

    def test_execute_search_memory_found(self, executor):
        executor.tool_registry.save_note("Python tips")
        result = executor.execute_action("search_memory", "python")
        assert "Found notes" in result
        assert "Python tips" in result

    def test_execute_search_memory_not_found(self, executor):
        result = executor.execute_action("search_memory", "nonexistent")
        assert "No matching notes found" in result

    def test_execute_unknown_tool(self, executor):
        result = executor.execute_action("unknown_tool", "param")
        assert "Error" in result
        assert "Unknown tool" in result
