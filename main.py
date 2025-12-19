# main.py
import os
from dotenv import load_dotenv
from agent.orchestrator import build_agent


def main():
    """Main entry point for the data analysis agent application."""
    
    # Load environment variables from .env file
    load_dotenv()
    
    # Validate API key exists
    api_key = os.getenv("OPENAI_API_KEY")
    if not api_key:
        raise EnvironmentError(
            "OPENAI_API_KEY not found in environment variables.\n"
            "Please create a .env file with: OPENAI_API_KEY=your-key-here"
        )
    
    print("=== Autonomous Data Analysis & Visualization Agent ===\n")

    # --- User inputs ---
    user_role = input("User role (admin / analyst / guest): ").strip().lower()
    if user_role not in ["admin", "analyst", "guest"]:
        print(f"Warning: '{user_role}' is not a recognized role. Proceeding anyway...")
    
    db_name = input("Database (northwind / chinook / sakila): ").strip().lower()
    valid_dbs = ["northwind", "chinook", "sakila"]
    if db_name not in valid_dbs:
        print(f"Warning: '{db_name}' not in {valid_dbs}. Proceeding anyway...")

    print("\nExample tasks:")
    print("  • List available tables")
    print("  • Give me a summary of the Customers table")
    print("  • Analyze missing values in Orders")
    print("  • Show correlation for Invoice table")
    print()

    task = input("Enter your task: ").strip()
    if not task:
        print("Error: Task cannot be empty.")
        return

    # --- Build agent ---
    print("\nInitializing agent...")
    try:
        agent = build_agent(api_key=api_key, temperature=0)
        print("✓ Agent built successfully.\n")
    except Exception as e:
        print(f"✗ Failed to build agent: {e}")
        return

    # --- Structured prompt ---
    prompt = f"""
You are a data analysis assistant with the following context:

User role: {user_role}
Database: {db_name}
Task: {task}

Please complete this task using the available tools. Be specific and thorough in your analysis.
""".strip()

    print("--- Prompt Sent to Agent ---")
    print(prompt)
    print("\n--- Agent Response ---\n")

    # --- Execute agent ---
    try:
        response = agent.invoke({"input": prompt})
        
        # Handle different response formats
        if isinstance(response, dict):
            output = response.get("output", response)
            print(output)
        else:
            print(response)
            
    except KeyboardInterrupt:
        print("\n\nTask interrupted by user.")
    except Exception as e:
        print(f"✗ Error during execution: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    main()