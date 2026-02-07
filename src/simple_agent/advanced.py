"""
Advanced Agent using Anthropic's Native Tool Use Feature.

Benefits over manual parsing:
- More reliable action extraction
- Better error handling
- Type validation
- Multi-tool orchestration
"""

from .base import BaseAgent
from .tools import TOOL_SCHEMAS

# Maximum number of consecutive tool-use loop iterations before stopping
MAX_TOOL_LOOP_ITERATIONS = 20
ALLOWED_TOOLS = {"calculate", "save_note", "search_memory"}


class AdvancedAgent(BaseAgent):
    """
    Advanced agent using Anthropic's native tool use API.

    Key improvements over SimpleAgent:
    - Uses Claude's tool use feature (no manual parsing needed)
    - Automatic tool schema validation
    - Better multi-turn tool interactions
    """

    def execute_tool(self, tool_name: str, tool_input: dict) -> dict:
        """
        Execute a tool by name with structured input.

        Validates tool name against an allowlist and checks that
        required input parameters are present and are strings.

        Args:
            tool_name: Name of the tool
            tool_input: Dict of input parameters

        Returns:
            Tool result as dict
        """
        if tool_name not in ALLOWED_TOOLS:
            return {"error": f"Unknown tool: {tool_name}"}

        if not isinstance(tool_input, dict):
            return {"error": "Tool input must be a dictionary"}

        if tool_name == "calculate":
            expression = tool_input.get("expression")
            if not isinstance(expression, str):
                return {"error": "Missing or invalid 'expression' parameter"}
            return self.tool_registry.calculate(expression)
        elif tool_name == "save_note":
            note = tool_input.get("note")
            if not isinstance(note, str):
                return {"error": "Missing or invalid 'note' parameter"}
            return self.tool_registry.save_note(note)
        elif tool_name == "search_memory":
            query = tool_input.get("query")
            if not isinstance(query, str):
                return {"error": "Missing or invalid 'query' parameter"}
            return self.tool_registry.search_memory(query)

        return {"error": f"Unknown tool: {tool_name}"}

    def run_step(self, user_input: str) -> tuple[str, list[dict]]:
        """
        Advanced agent loop with native tool use.

        Process:
        1. OBSERVE: Add user input to conversation
        2. THINK: Query Claude with tool definitions
        3. ACT: Execute tools if requested, loop until final answer

        Args:
            user_input: The user's message

        Returns:
            Tuple of (response_text, tool_results)
        """
        print("\n[Observe] Received user input")

        self.conversation_history.append({"role": "user", "content": user_input})

        tool_results = []
        iterations = 0

        # Agent loop: continue until we get a text response
        while True:
            iterations += 1
            if iterations > MAX_TOOL_LOOP_ITERATIONS:
                self._trim_history()
                return (
                    "Stopped: too many consecutive tool calls.",
                    tool_results,
                )
            print("[Think] Querying LLM with tool definitions...")

            response = self.client.messages.create(
                model=self.model,
                max_tokens=1024,
                tools=TOOL_SCHEMAS,
                messages=self.conversation_history,
            )

            if response.stop_reason == "end_turn":
                # Claude provided a final text response
                text_response = next(
                    (block.text for block in response.content if block.type == "text"),
                    "",
                )
                self.conversation_history.append(
                    {"role": "assistant", "content": response.content}
                )
                # Trim history to prevent unbounded growth
                self._trim_history()
                return text_response, tool_results

            elif response.stop_reason == "tool_use":
                # Claude wants to use tools
                print("[Act] Executing requested tools...")

                self.conversation_history.append(
                    {"role": "assistant", "content": response.content}
                )

                tool_results_content = []

                for block in response.content:
                    if block.type == "tool_use":
                        tool_name = block.name
                        tool_input = block.input

                        print(f"   -> {tool_name}: {tool_input}")

                        result = self.execute_tool(tool_name, tool_input)
                        tool_results.append(
                            {"tool": tool_name, "input": tool_input, "output": result}
                        )

                        tool_results_content.append(
                            {
                                "type": "tool_result",
                                "tool_use_id": block.id,
                                "content": str(result),
                            }
                        )

                self.conversation_history.append(
                    {"role": "user", "content": tool_results_content}
                )
                # Trim history to prevent unbounded growth during tool loops
                self._trim_history()
                # Loop continues to process tool results

            else:
                self._trim_history()
                return f"Unexpected stop reason: {response.stop_reason}", tool_results

    def _get_banner(self) -> str:
        return "Advanced Agent (Native Tool Use)"

    def _print_action_result(self, result: dict):
        """Print a tool result."""
        print(f"   {result['tool']}: {result['output']}")


def compare_approaches():
    """Show comparison between manual parsing and native tool use."""
    print("\n" + "=" * 60)
    print("Comparison: Manual Parsing vs. Native Tool Use")
    print("=" * 60)

    print("\nManual Parsing (SimpleAgent):")
    print("  + Simple to understand")
    print("  + Full control over parsing")
    print("  - Requires careful prompt engineering")
    print("  - LLM might not follow format exactly")

    print("\nNative Tool Use (AdvancedAgent):")
    print("  + Structured tool definitions")
    print("  + Automatic validation")
    print("  + Better multi-tool orchestration")
    print("  + More reliable")

    print("\nRecommendation:")
    print("  - SimpleAgent: Learning and prototypes")
    print("  - AdvancedAgent: Production applications")


def main():
    """Main entry point for the advanced agent."""
    compare_approaches()

    try:
        agent = AdvancedAgent()
        agent.run_interactive()
    except ValueError as e:
        print(f"\nError: {e}")
        print("Please set your ANTHROPIC_API_KEY in a .env file")


if __name__ == "__main__":
    main()
