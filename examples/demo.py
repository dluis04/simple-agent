"""
Example usage of the Simple Agent.
Demonstrates programmatic interaction with the agent.
"""

import os
import sys

# Add src to path for direct execution
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "src"))

from simple_agent import SimpleAgent  # noqa: E402


def demo_agent():
    """Demonstrate the agent with a series of predefined interactions."""

    print("=" * 60)
    print("Simple Agent - Programmatic Demo")
    print("=" * 60)

    if not os.getenv("ANTHROPIC_API_KEY"):
        print("\nError: ANTHROPIC_API_KEY not found in environment")
        print("Please create a .env file with your API key")
        return

    agent = SimpleAgent()

    demo_conversations = [
        "Hello! What can you do?",
        "Calculate 123 * 456",
        "Remember that my favorite color is blue",
        "Save a note: Call dentist on Friday",
        "What's 2^10?",
        "What do you remember about my favorite color?",
        "Search your memory for dentist",
    ]

    for i, user_input in enumerate(demo_conversations, 1):
        print(f"\n{'=' * 60}")
        print(f"Interaction {i}/{len(demo_conversations)}")
        print(f"{'=' * 60}")
        print(f"\n>> User: {user_input}")

        try:
            response, action_results = agent.run_step(user_input)

            if action_results:
                print("\n[Actions]")
                for result in action_results:
                    print(f"   {result}")

            if response:
                print(f"\n>> Agent: {response}")

        except Exception as e:
            print(f"\nError: {e}")

    print(f"\n\n{'=' * 60}")
    print("Demo Complete!")
    print(f"{'=' * 60}")
    print(f"\nProcessed {len(demo_conversations)} interactions")
    print(f"Memory contains {len(agent.memory)} saved notes:")
    for note in agent.memory:
        print(f"  - {note}")


def custom_agent_example():
    """Example of creating a custom agent with extended tools."""
    print("\n" + "=" * 60)
    print("Custom Agent Example")
    print("=" * 60)

    class CustomAgent(SimpleAgent):
        """Extended agent with custom tools."""

        def __init__(self):
            super().__init__()

        def execute_action(self, tool_name: str, parameter: str) -> str:
            # Handle custom tool
            if tool_name == "uppercase":
                return f"Uppercase: {parameter.upper()}"
            # Delegate to parent for standard tools
            return super().execute_action(tool_name, parameter)

        def get_system_prompt(self):
            base_prompt = super().get_system_prompt()
            return base_prompt + "\n- uppercase: Convert text to uppercase"

    if os.getenv("ANTHROPIC_API_KEY"):
        agent = CustomAgent()
        print("\n>> User: Convert 'hello world' to uppercase")
        response, results = agent.run_step("Convert 'hello world' to uppercase")

        if results:
            print("\n[Actions]")
            for result in results:
                print(f"   {result}")
        if response:
            print(f"\n>> Agent: {response}")


if __name__ == "__main__":
    from dotenv import load_dotenv

    load_dotenv()

    demo_agent()
    custom_agent_example()
