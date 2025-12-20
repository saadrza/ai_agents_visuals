# main.py
import os
import sys
from typing import Any, Dict, Optional
from dotenv import load_dotenv
from agent.orchestrator import build_agent

# --- Configuration ---
DATABASES = {
    "northwind": "database/northwind_small.sqlite",
    "chinook": "database/chinook.db",
    "sakila": "database/sakila.db"
}

DEFAULT_MODEL = "gpt-4o"

def _extract_output(response: Any) -> str:
    """
    Parses the agent response to handle both LangGraph (dict) 
    and legacy LangChain (str/dict) formats.
    """
    # 1. Handle LangGraph / OpenAI Dictionary format
    if isinstance(response, dict) and "messages" in response:
        final_message = response["messages"][-1]
        return getattr(final_message, 'content', str(final_message))
    
    # 2. Handle Classic LangChain Dictionary
    if isinstance(response, dict):
        return response.get("output", str(response))
    
    # 3. Handle Direct String Output
    return str(response)

def setup_environment() -> str:
    """Loads environment variables and validates API key."""
    load_dotenv()
    api_key = os.getenv("OPENAI_API_KEY")
    if not api_key:
        print("Error: OPENAI_API_KEY not found in environment variables.")
        print("Please create a .env file with: OPENAI_API_KEY=your-key-here")
        sys.exit(1)
    return api_key

def select_database() -> str:
    """Prompts user to select and validate a database."""
    print(f"\nAvailable databases: {', '.join(DATABASES.keys())}")
    
    while True:
        db_name = input("Select Database: ").strip().lower()
        if db_name in DATABASES:
            db_path = os.path.abspath(DATABASES[db_name])
            if os.path.exists(db_path):
                return db_path
            print(f"Error: File not found at {db_path}")
        else:
            print(f"Invalid selection. Choose from: {list(DATABASES.keys())}")

def main():
    """Main execution loop for the data analysis agent."""
    print("=== Autonomous Data Analysis & Visualization Agent ===\n")
    
    api_key = setup_environment()
    
    # User Inputs
    user_role = input("User role (admin / analyst / guest): ").strip().lower() or "analyst"
    db_path = select_database()

    # Initialize Agent
    print("\nInitializing agent...")
    try:
        agent = build_agent(
            api_key=api_key, 
            temperature=0, 
            model=os.getenv("OPENAI_MODEL", DEFAULT_MODEL),
            db_path=db_path
        )
        print("✓ Agent ready. (Type 'exit' or 'q' to quit)\n")
    except Exception as e:
        print(f"✗ Critical Error: Failed to build agent.\n{e}")
        return

    # REPL Loop (Read-Eval-Print Loop)
    while True:
        try:
            task = input("\nOnly_Analyst> ").strip()
            if task.lower() in ['exit', 'quit', 'q']:
                print("Goodbye!")
                break
            if not task:
                continue

            # Construct Prompt
            prompt = (
                f"User role: {user_role}\n"
                f"Database Path: {db_path}\n"
                f"Task: {task}\n"
                "Please analyze the data and provide a concise answer."
            )

            # Execute
            print("Thinking...")
            
            # Detect invocation method (invoke vs __call__)
            if hasattr(agent, 'invoke'):
                # Try LangGraph format first, fall back to simple input
                try:
                    raw_response = agent.invoke({"messages": [("user", prompt)]})
                except (TypeError, ValueError):
                    raw_response = agent.invoke({"input": prompt})
            else:
                raw_response = agent(prompt)

            # Output
            final_answer = _extract_output(raw_response)
            print("-" * 60)
            print(final_answer)
            print("-" * 60)

        except KeyboardInterrupt:
            print("\nOperation cancelled by user.")
        except Exception as e:
            print(f"Error during execution: {e}")

if __name__ == "__main__":
    main()