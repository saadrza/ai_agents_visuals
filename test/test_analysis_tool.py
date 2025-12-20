# test_agent.py
"""
Automated testing script for the Data Analysis Agent
Run this to test various capabilities without manual input
"""

import os
from dotenv import load_dotenv
from agent.orchestrator import build_agent


# Test cases with expected behaviors
TEST_CASES = [
    {
        "name": "List Tables",
        "task": "List all available tables in the database",
        "db": "northwind",
        "expected": "Should list all tables"
    },
    {
        "name": "Schema Analysis",
        "task": "Show me the schema of the Customer table",
        "db": "northwind",
        "expected": "Should show column names and types"
    },
    {
        "name": "Simple Query",
        "task": "Show me the top 5 products by unit price",
        "db": "northwind",
        "expected": "Should return 5 products with prices"
    },
    {
        "name": "Count Query",
        "task": "How many customers are there in total?",
        "db": "northwind",
        "expected": "Should return a number"
    },
    {
        "name": "Aggregation",
        "task": "What is the total number of orders in the database?",
        "db": "northwind",
        "expected": "Should return order count"
    },
    {
        "name": "Top Customers",
        "task": "Show me the top 5 customers by number of orders",
        "db": "northwind",
        "expected": "Should show customers with order counts"
    },
    {
        "name": "Category Analysis",
        "task": "How many products are in each category?",
        "db": "northwind",
        "expected": "Should group products by category"
    },
    {
        "name": "Date Analysis",
        "task": "Show me the number of orders per year",
        "db": "northwind",
        "expected": "Should show yearly order counts"
    },
    {
        "name": "Employee Performance",
        "task": "Which employee has processed the most orders?",
        "db": "northwind",
        "expected": "Should identify top employee"
    },
    {
        "name": "Visualization",
        "task": "Create a bar chart showing products by category",
        "db": "northwind",
        "expected": "Should create and save a chart"
    }
]


def run_test(agent, test_case, db_path):
    """Run a single test case."""
    print("\n" + "="*70)
    print(f"TEST: {test_case['name']}")
    print("="*70)
    print(f"Task: {test_case['task']}")
    print(f"Expected: {test_case['expected']}")
    print("-"*70)
    
    prompt = f"""
You are a data analysis assistant.

Database: {test_case['db']} (SQLite file: {db_path})
Task: {test_case['task']}

Please complete this task using the available tools.
"""
    
    try:
        response = agent.invoke({"messages": [("user", prompt)]})
        
        # Extract final message
        if isinstance(response, dict) and "messages" in response:
            final_message = response["messages"][-1]
            output = final_message.content if hasattr(final_message, 'content') else str(final_message)
        else:
            output = str(response)
        
        print("\nRESULT:")
        print(output[:500] + "..." if len(output) > 500 else output)
        print("\n✓ TEST PASSED")
        return True
        
    except Exception as e:
        print(f"\n✗ TEST FAILED: {e}")
        return False


def main():
    """Run all tests."""
    load_dotenv()
    
    api_key = os.getenv("OPENAI_API_KEY")
    if not api_key:
        print("Error: OPENAI_API_KEY not found in .env file")
        return
    
    print("="*70)
    print("DATA ANALYSIS AGENT - AUTOMATED TEST SUITE")
    print("="*70)
    
    # Initialize agent once
    db_path = "database/northwind_small.sqlite"
    
    if not os.path.exists(db_path):
        print(f"Error: Database not found at {db_path}")
        return
    
    print("\nInitializing agent...")
    try:
        agent = build_agent(
            api_key=api_key,
            temperature=0,
            model="gpt-4o",
            db_path=db_path
        )
        print("✓ Agent initialized successfully\n")
    except Exception as e:
        print(f"✗ Failed to initialize agent: {e}")
        return
    
    # Run tests
    results = []
    for i, test_case in enumerate(TEST_CASES, 1):
        print(f"\nRunning test {i}/{len(TEST_CASES)}...")
        result = run_test(agent, test_case, db_path)
        results.append((test_case['name'], result))
        
        # Small delay between tests
        import time
        time.sleep(2)
    
    # Summary
    print("\n" + "="*70)
    print("TEST SUMMARY")
    print("="*70)
    
    passed = sum(1 for _, result in results if result)
    total = len(results)
    
    for name, result in results:
        status = "✓ PASS" if result else "✗ FAIL"
        print(f"{status}: {name}")
    
    print(f"\nTotal: {passed}/{total} tests passed ({passed/total*100:.1f}%)")
    
    if passed == total:
        print("\n🎉 All tests passed! Agent is working perfectly.")
    else:
        print(f"\n⚠️ {total - passed} test(s) failed. Check the output above.")


if __name__ == "__main__":
    main()