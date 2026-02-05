"""
Reusable tools for the conversational agents.
"""

import ast
import operator
from typing import Union


class SafeExpressionEvaluator:
    """
    Safely evaluate mathematical expressions using AST parsing.
    Only allows numbers and basic arithmetic operators.
    """

    OPERATORS = {
        ast.Add: operator.add,
        ast.Sub: operator.sub,
        ast.Mult: operator.mul,
        ast.Div: operator.truediv,
        ast.Pow: operator.pow,
        ast.USub: operator.neg,
        ast.UAdd: operator.pos,
    }

    MAX_POWER = 1000  # Prevent excessive computation

    def evaluate(self, expression: str) -> Union[int, float]:
        """
        Safely evaluate a mathematical expression.

        Args:
            expression: Mathematical expression string

        Returns:
            The computed result

        Raises:
            ValueError: If the expression contains disallowed constructs
        """
        if not expression or not expression.strip():
            raise ValueError("Empty expression")

        # Replace ^ with ** for exponentiation
        expression = expression.replace("^", "**")

        try:
            tree = ast.parse(expression, mode="eval")
        except SyntaxError as e:
            raise ValueError(f"Invalid syntax: {e}")

        return self._eval_node(tree.body)

    def _eval_node(self, node: ast.AST) -> Union[int, float]:
        """Recursively evaluate an AST node."""
        if isinstance(node, ast.Constant):
            if isinstance(node.value, (int, float)):
                return node.value
            raise ValueError(f"Unsupported constant type: {type(node.value).__name__}")

        elif isinstance(node, ast.BinOp):
            left = self._eval_node(node.left)
            right = self._eval_node(node.right)
            op_func = self.OPERATORS.get(type(node.op))
            if op_func is None:
                raise ValueError(f"Unsupported operator: {type(node.op).__name__}")

            # Prevent excessive computation with large exponents
            if isinstance(node.op, ast.Pow):
                if isinstance(right, (int, float)) and abs(right) > self.MAX_POWER:
                    raise ValueError(f"Exponent too large (max {self.MAX_POWER})")

            return op_func(left, right)

        elif isinstance(node, ast.UnaryOp):
            operand = self._eval_node(node.operand)
            op_func = self.OPERATORS.get(type(node.op))
            if op_func is None:
                raise ValueError(f"Unsupported unary operator: {type(node.op).__name__}")
            return op_func(operand)

        elif isinstance(node, ast.Expression):
            return self._eval_node(node.body)

        else:
            raise ValueError(f"Unsupported expression type: {type(node).__name__}")


class ToolRegistry:
    """Registry of available tools with their implementations."""

    def __init__(self):
        self.memory: list[str] = []
        self._evaluator = SafeExpressionEvaluator()

    def calculate(self, expression: str) -> dict:
        """
        Perform mathematical calculation using safe AST-based evaluation.

        Args:
            expression: Mathematical expression to evaluate

        Returns:
            Dict with result or error
        """
        try:
            result = self._evaluator.evaluate(expression)
            return {"result": result}
        except ValueError as e:
            return {"error": str(e)}
        except ZeroDivisionError:
            return {"error": "Division by zero"}
        except Exception as e:
            return {"error": f"Calculation error: {str(e)}"}

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
