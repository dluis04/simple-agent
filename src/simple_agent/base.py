"""
Base agent class with shared functionality.
"""

import os
from abc import ABC, abstractmethod

from anthropic import Anthropic
from dotenv import load_dotenv

from .tools import ToolRegistry

load_dotenv()

# Maximum length of user input accepted by the interactive loop
MAX_INPUT_LENGTH = 10000


class BaseAgent(ABC):
    """
    Abstract base class for conversational agents.

    Provides:
    - Anthropic client initialization
    - Conversation history management
    - Tool registry
    - Interactive run loop
    """

    def __init__(
        self, model: str = "claude-sonnet-4-20250514", max_history_length: int = 50
    ):
        """
        Initialize the agent with Anthropic client.

        Args:
            model: The Claude model to use
            max_history_length: Maximum number of messages to keep in history.
                               Uses a sliding window to prevent unbounded growth.
                               Set to 0 for unlimited history (not recommended).
        """
        api_key = os.getenv("ANTHROPIC_API_KEY")
        if not api_key:
            raise ValueError("ANTHROPIC_API_KEY not found in environment variables")

        self.client = Anthropic(api_key=api_key)
        self.model = model
        self.max_history_length = max_history_length
        self.conversation_history: list[dict] = []
        self.tool_registry = ToolRegistry()

    @property
    def memory(self) -> list[str]:
        """Access to tool registry memory."""
        return self.tool_registry.memory

    def clear_history(self) -> None:
        """Clear conversation history for manual control."""
        self.conversation_history.clear()

    def _trim_history(self) -> None:
        """
        Trim conversation history to max_history_length using a sliding window.

        Keeps the most recent messages while preserving conversation coherence.
        Always starts with a user message to maintain valid message structure.
        """
        if self.max_history_length <= 0:
            return  # Unlimited history

        if len(self.conversation_history) <= self.max_history_length:
            return  # No trimming needed

        # Calculate how many messages to remove
        excess = len(self.conversation_history) - self.max_history_length

        # Trim from the beginning, but ensure we start with a user message
        self.conversation_history = self.conversation_history[excess:]

        # Ensure history starts with a user message for valid API structure
        while (
            self.conversation_history and self.conversation_history[0]["role"] != "user"
        ):
            self.conversation_history.pop(0)

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

                if len(user_input) > MAX_INPUT_LENGTH:
                    print(
                        f"\nInput too long (max {MAX_INPUT_LENGTH} characters). "
                        "Please shorten your message."
                    )
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
