# main.py
import os
from dotenv import load_dotenv
from agent.orchestrator import build_agent


# Database mapping
DATABASES = {
    "northwind": "database/northwind_small.sqlite",
    "chinook": "database/chinook.db",
    "sakila": "database/sakila.db"
}


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
    
    print(f"\nAvailable databases: {', '.join(DATABASES.keys())}")
    db_name = input("Database: ").strip().lower()
    
    if db_name not in DATABASES:
        print(f"Error: '{db_name}' not in available databases: {list(DATABASES.keys())}")
        return
    
    # Get the full database path
    db_path = DATABASES[db_name]
    
    # Verify database file exists
    if not os.path.exists(db_path):
        print(f"Error: Database file '{db_path}' not found!")
        print(f"Please ensure the database file exists at: {os.path.abspath(db_path)}")
        return

    print("\nExample tasks:")
    print("  • List available tables")
    print("  • Give me a summary of the Customers table")
    print("  • Show me the top 10 customers by total purchases")
    print("  • Analyze sales trends over time")
    print("  • Create a visualization of product categories")
    print()

    task = input("Enter your task: ").strip()
    if not task:
        print("Error: Task cannot be empty.")
        return

    # --- Build agent ---
    print("\nInitializing agent...")
    try:
        agent = build_agent(
            api_key=api_key, 
            temperature=0, 
            model="gpt-4o",
            db_path=db_path  # Pass the specific database file path
        )
        print("✓ Agent built successfully.\n")
    except Exception as e:
        print(f"✗ Failed to build agent: {e}")
        import traceback
        traceback.print_exc()
        return

    # --- Structured prompt ---
    prompt = f"""
You are a data analysis assistant with the following context:

User role: {user_role}
Database: {db_name} (SQLite file: {db_path})
Task: {task}

Please complete this task using the available tools. Always start by understanding the database schema if needed.
Be specific and thorough in your analysis.
""".strip()

    print("--- Prompt Sent to Agent ---")
    print(prompt)
    print("\n--- Agent Response ---\n")

    # --- Execute agent ---
    try:
        # Check if it's a LangGraph agent or classic LangChain agent
        if hasattr(agent, 'invoke'):
            # Try to determine the format by checking the signature
            try:
                # Try LangGraph format first
                response = agent.invoke({"messages": [("user", prompt)]})
                
                # Handle LangGraph response
                if isinstance(response, dict) and "messages" in response:
                    final_message = response["messages"][-1]
                    if hasattr(final_message, 'content'):
                        output = final_message.content
                    else:
                        output = str(final_message)
                else:
                    output = str(response)
                    
            except (TypeError, KeyError):
                # Fall back to classic LangChain format
                response = agent.invoke({"input": prompt})
                
                # Handle classic LangChain response
                if isinstance(response, dict):
                    output = response.get("output", str(response))
                else:
                    output = str(response)
        else:
            # Very old API - direct call
            output = agent(prompt)
        
        # Print final answer
        print("\n" + "="*60)
        print("FINAL ANSWER:")
        print("="*60)
        print(output)
            
    except KeyboardInterrupt:
        print("\n\nTask interrupted by user.")
    except Exception as e:
        print(f"✗ Error during execution: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    main()