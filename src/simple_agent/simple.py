"""
Simple Conversational Agent with manual action parsing.
Demonstrates the basic agent loop: Observe -> Think -> Act
"""

from .base import BaseAgent

# --- Validation constants for action parsing ---
MAX_ACTIONS_PER_RESPONSE = 10  # Maximum actions parsed from a single LLM response
MAX_PARAMETER_LENGTH = 1000  # Maximum length of a single action parameter
ALLOWED_TOOLS = {"calculate", "save_note", "search_memory"}


class SimpleAgent(BaseAgent):
    """
    A basic conversational agent that uses manual parsing to extract actions.

    The agent follows a simple loop:
    1. OBSERVE: Receive user input
    2. THINK: Send to LLM with appropriate prompt
    3. ACT: Parse response and execute actions
    """

    def get_system_prompt(self) -> str:
        """
        System prompt that defines agent behavior and available tools.

        The LLM is instructed to output actions in a specific format
        that we can parse: ACTION: tool_name: parameter
        """
        return """You are a helpful AI assistant with the ability to perform actions.

You have access to the following tools:
- calculate: Perform mathematical calculations (e.g., "calculate: 5 + 3 * 2")
- search_memory: Search through saved notes (e.g., "search_memory: keyword")
- save_note: Save information for later (e.g., "save_note: Important meeting at 3pm")

When you want to use a tool, format your response like this:
ACTION: tool_name: parameter

You can also respond conversationally without using any tools.

Be helpful, concise, and friendly. If a user asks you to remember something,
use save_note. If they ask about something you saved, use search_memory."""

    def parse_actions(self, response_text: str) -> list[tuple[str, str]]:
        """
        Extract actions from LLM response with validation.

        Looks for lines starting with "ACTION:" and extracts tool name and parameter.
        Validates tool names against an allowlist and enforces limits on
        the number of actions and parameter length.

        Args:
            response_text: The LLM's response

        Returns:
            List of (tool_name, parameter) tuples
        """
        actions = []

        for line in response_text.split("\n"):
            if line.strip().startswith("ACTION:"):
                if len(actions) >= MAX_ACTIONS_PER_RESPONSE:
                    break

                action_part = line.strip()[7:].strip()  # Remove 'ACTION:'
                if ":" in action_part:
                    tool_name, parameter = action_part.split(":", 1)
                    tool_name = tool_name.strip()
                    parameter = parameter.strip()

                    # Validate tool name against allowlist
                    if tool_name not in ALLOWED_TOOLS:
                        continue

                    # Truncate overly long parameters
                    if len(parameter) > MAX_PARAMETER_LENGTH:
                        parameter = parameter[:MAX_PARAMETER_LENGTH]

                    actions.append((tool_name, parameter))

        return actions

    def execute_action(self, tool_name: str, parameter: str) -> str:
        """
        Execute a tool action.

        Args:
            tool_name: Name of the tool to execute
            parameter: Parameter to pass to the tool

        Returns:
            Result string
        """
        if tool_name == "calculate":
            result = self.tool_registry.calculate(parameter)
            if "error" in result:
                return f"Error: {result['error']}"
            return f"Result: {result['result']}"

        elif tool_name == "save_note":
            result = self.tool_registry.save_note(parameter)
            return f"Saved note: {parameter}"

        elif tool_name == "search_memory":
            result = self.tool_registry.search_memory(parameter)
            if result["count"] > 0:
                return "Found notes:\n" + "\n".join(f"- {n}" for n in result["results"])
            return "No matching notes found."

        return f"Error: Unknown tool '{tool_name}'"

    def think(self, user_input: str) -> str:
        """
        THINK step: Send input to LLM with conversation history.

        Args:
            user_input: The user's message

        Returns:
            The LLM's response text
        """
        self.conversation_history.append({"role": "user", "content": user_input})

        response = self.client.messages.create(
            model=self.model,
            max_tokens=1024,
            system=self.get_system_prompt(),
            messages=self.conversation_history,
        )

        response_text = response.content[0].text

        self.conversation_history.append(
            {"role": "assistant", "content": response_text}
        )

        # Trim history to prevent unbounded growth
        self._trim_history()

        return response_text

    def act(self, response_text: str) -> tuple[str, list[str]]:
        """
        ACT step: Parse and execute actions from LLM response.

        Args:
            response_text: The LLM's response

        Returns:
            Tuple of (display_text, action_results)
        """
        actions = self.parse_actions(response_text)
        action_results = []

        for tool_name, parameter in actions:
            result = self.execute_action(tool_name, parameter)
            action_results.append(result)

        # Remove ACTION: lines from display
        display_text = "\n".join(
            line
            for line in response_text.split("\n")
            if not line.strip().startswith("ACTION:")
        ).strip()

        return display_text, action_results

    def run_step(self, user_input: str) -> tuple[str, list[str]]:
        """
        The basic agent loop: Observe -> Think -> Act

        Args:
            user_input: The user's message

        Returns:
            Tuple of (response_text, action_results)
        """
        # OBSERVE
        print("\n[Observe] Received user input")

        # THINK
        print("[Think] Querying LLM...")
        response_text = self.think(user_input)

        # ACT
        print("[Act] Parsing and executing actions...")
        display_text, action_results = self.act(response_text)

        return display_text, action_results

    def _get_banner(self) -> str:
        return "Simple Agent (Manual Parsing)"


def main():
    """Main entry point for the simple agent."""
    try:
        agent = SimpleAgent()
        agent.run_interactive()
    except ValueError as e:
        print(f"Error: {e}")
        print("\nPlease set your ANTHROPIC_API_KEY in a .env file")


if __name__ == "__main__":
    main()
