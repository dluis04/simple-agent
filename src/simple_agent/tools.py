"""
Reusable tools for the conversational agents.
"""

import re


class ToolRegistry:
    """Registry of available tools with their implementations."""

    def __init__(self):
        self.memory: list[str] = []

    def calculate(self, expression: str) -> dict:
        """
        Perform mathematical calculation.

        Args:
            expression: Mathematical expression to evaluate

        Returns:
            Dict with result or error
        """
        try:
            # Replace ^ with ** for Python exponentiation
            expression = expression.replace("^", "**")

            # Safety: only allow numbers and operators
            if not re.match(r"^[\d\s+\-*/().]+$", expression):
                return {"error": "Invalid expression"}

            result = eval(expression)
            return {"result": result}
        except Exception as e:
            return {"error": str(e)}

    def save_note(self, note: str) -> dict:
        """
        Save a note to memory.

        Args:
            note: The note to save

        Returns:
            Dict with status and message
        """
        self.memory.append(note)
        return {"status": "success", "message": f"Saved: {note}"}

    def search_memory(self, query: str) -> dict:
        """
        Search through saved notes.

        Args:
            query: Keyword to search for

        Returns:
            Dict with results and count
        """
        results = [note for note in self.memory if query.lower() in note.lower()]
        return {"results": results, "count": len(results)}


# Tool schemas for Anthropic's native tool use
TOOL_SCHEMAS = [
    {
        "name": "calculate",
        "description": "Perform math calculations. Supports +, -, *, /, ^, ()",
        "input_schema": {
            "type": "object",
            "properties": {
                "expression": {
                    "type": "string",
                    "description": "Math expression to evaluate (e.g., '5 + 3 * 2')",
                }
            },
            "required": ["expression"],
        },
    },
    {
        "name": "save_note",
        "description": "Save a note to memory for later retrieval.",
        "input_schema": {
            "type": "object",
            "properties": {
                "note": {
                    "type": "string",
                    "description": "The note or information to save",
                }
            },
            "required": ["note"],
        },
    },
    {
        "name": "search_memory",
        "description": "Search through previously saved notes.",
        "input_schema": {
            "type": "object",
            "properties": {
                "query": {
                    "type": "string",
                    "description": "The keyword or phrase to search for",
                }
            },
            "required": ["query"],
        },
    },
]
