"""Tests for ToolRegistry."""

import pytest

from simple_agent.tools import ToolRegistry, TOOL_SCHEMAS


class TestToolRegistry:
    """Tests for the ToolRegistry class."""

    @pytest.fixture
    def registry(self):
        """Create a fresh ToolRegistry for each test."""
        return ToolRegistry()

    # --- calculate tests ---

    def test_calculate_simple_addition(self, registry):
        result = registry.calculate("2 + 3")
        assert result == {"result": 5}

    def test_calculate_multiplication(self, registry):
        result = registry.calculate("5 * 7")
        assert result == {"result": 35}

    def test_calculate_complex_expression(self, registry):
        result = registry.calculate("(10 + 5) * 2")
        assert result == {"result": 30}

    def test_calculate_with_exponent(self, registry):
        result = registry.calculate("2^3")
        assert result == {"result": 8}

    def test_calculate_division(self, registry):
        result = registry.calculate("15 / 3")
        assert result == {"result": 5.0}

    def test_calculate_invalid_expression(self, registry):
        result = registry.calculate("5 + abc")
        assert "error" in result

    def test_calculate_empty_expression(self, registry):
        result = registry.calculate("")
        assert "error" in result

    # --- save_note tests ---

    def test_save_note_success(self, registry):
        result = registry.save_note("Buy milk")
        assert result["status"] == "success"
        assert "Buy milk" in result["message"]

    def test_save_note_adds_to_memory(self, registry):
        registry.save_note("First note")
        registry.save_note("Second note")
        assert len(registry.memory) == 2
        assert "First note" in registry.memory
        assert "Second note" in registry.memory

    # --- search_memory tests ---

    def test_search_memory_finds_match(self, registry):
        registry.save_note("Meeting at 3pm")
        registry.save_note("Call mom")
        result = registry.search_memory("meeting")
        assert result["count"] == 1
        assert "Meeting at 3pm" in result["results"]

    def test_search_memory_case_insensitive(self, registry):
        registry.save_note("IMPORTANT: deadline tomorrow")
        result = registry.search_memory("important")
        assert result["count"] == 1

    def test_search_memory_no_match(self, registry):
        registry.save_note("Buy groceries")
        result = registry.search_memory("meeting")
        assert result["count"] == 0
        assert result["results"] == []

    def test_search_memory_empty(self, registry):
        result = registry.search_memory("anything")
        assert result["count"] == 0

    def test_search_memory_multiple_matches(self, registry):
        registry.save_note("Python tutorial")
        registry.save_note("Python debugging tips")
        registry.save_note("JavaScript basics")
        result = registry.search_memory("python")
        assert result["count"] == 2


class TestToolSchemas:
    """Tests for TOOL_SCHEMAS structure."""

    def test_all_tools_have_required_fields(self):
        required_fields = ["name", "description", "input_schema"]
        for schema in TOOL_SCHEMAS:
            for field in required_fields:
                assert field in schema, f"Tool missing {field}"

    def test_tool_names(self):
        names = [schema["name"] for schema in TOOL_SCHEMAS]
        assert "calculate" in names
        assert "save_note" in names
        assert "search_memory" in names

    def test_input_schemas_have_properties(self):
        for schema in TOOL_SCHEMAS:
            assert "properties" in schema["input_schema"]
            assert "required" in schema["input_schema"]
