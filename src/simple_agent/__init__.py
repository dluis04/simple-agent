"""
Simple Agent - A conversational AI agent framework.

Two implementations available:
- SimpleAgent: Manual parsing approach (educational)
- AdvancedAgent: Native tool use (production)
"""

from .base import ActionResult
from .simple import SimpleAgent
from .advanced import AdvancedAgent
from .tools import ToolRegistry, TOOL_SCHEMAS

__all__ = ["SimpleAgent", "AdvancedAgent", "ToolRegistry", "TOOL_SCHEMAS", "ActionResult"]
