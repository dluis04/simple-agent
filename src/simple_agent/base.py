"""
Base agent class with shared functionality.
"""

import os
from abc import ABC, abstractmethod

from anthropic import Anthropic
from dotenv import load_dotenv

from .tools import ToolRegistry

load_dotenv()


class BaseAgent(ABC):
    """
    Abstract base class for conversational agents.

    Provides:
    - Anthropic client initialization
    - Conversation history management
    - Tool registry
    - Interactive run loop
    """

    def __init__(self, model: str = "claude-sonnet-4-20250514"):
        """Initialize the agent with Anthropic client."""
        api_key = os.getenv("ANTHROPIC_API_KEY")
        if not api_key:
            raise ValueError("ANTHROPIC_API_KEY not found in environment variables")

        self.client = Anthropic(api_key=api_key)
        self.model = model
        self.conversation_history: list[dict] = []
        self.tool_registry = ToolRegistry()

    @property
    def memory(self) -> list[str]:
        """Access to tool registry memory."""
        return self.tool_registry.memory

    @abstractmethod
    def run_step(self, user_input: str) -> tuple[str, list]:
        """
        Process a single user input through the agent loop.

        Args:
            user_input: The user's message

        Returns:
            Tuple of (response_text, action_results)
        """
        pass

    def run_interactive(self):
        """Run the agent in interactive mode."""
        print("=" * 60)
        print(self._get_banner())
        print("=" * 60)
        print("Type 'quit' or 'exit' to end the conversation")
        print("Try: 'Calculate 15 * 7' or 'Remember to buy milk'\n")

        while True:
            try:
                user_input = input("\n>> You: ").strip()

                if user_input.lower() in ["quit", "exit", "q"]:
                    print("\nGoodbye!")
                    break

                if not user_input:
                    continue

                response, action_results = self.run_step(user_input)

                if action_results:
                    print("\n[Actions]")
                    for result in action_results:
                        self._print_action_result(result)

                if response:
                    print(f"\n>> Agent: {response}")

            except KeyboardInterrupt:
                print("\n\nGoodbye!")
                break
            except Exception as e:
                print(f"\nError: {e}")

    def _get_banner(self) -> str:
        """Get the banner text for interactive mode."""
        return "Conversational Agent"

    def _print_action_result(self, result):
        """Print a single action result."""
        print(f"   {result}")
