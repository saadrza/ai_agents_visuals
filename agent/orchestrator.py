# agent/orchestrator.py
from langchain_openai import ChatOpenAI

from tools.analysis_tool import DataAnalysisTool
from tools.schema_tool import SchemaTool
from tools.visualization_tool import VisualizationTool


def build_agent(
    api_key: str = None, 
    temperature: float = 0, 
    model: str = "gpt-4o",
    db_path: str = None
):
    """
    Build and return a LangChain agent executor with data analysis tools.
    
    Args:
        api_key: OpenAI API key (optional, can use env var)
        temperature: LLM temperature for response randomness
        model: OpenAI model to use (default: gpt-4o)
        db_path: Path to SQLite database file
        
    Returns:
        Configured agent executor
    """
    try:
        if not db_path:
            raise ValueError("db_path is required for database operations")
        
        # --- Initialize Tools ---
        tools = [
            SchemaTool(db_path=db_path),
            DataAnalysisTool(db_path=db_path),
            VisualizationTool(db_path=db_path),
        ]
        
        # Validate tools
        if not all(tools):
            raise ValueError("One or more tools failed to initialize")

        # --- Initialize LLM ---
        llm = ChatOpenAI(
            model=model,
            temperature=temperature,
            api_key=api_key
        )

        # Try LangGraph first (most modern and compatible)
        try:
            from langgraph.prebuilt import create_react_agent
            
            # Create system message that teaches the LLM about SQL reserved words
            system_message = """You are a helpful data analysis assistant with access to a SQLite database.

                                CRITICAL SQL SYNTAX RULES:
                                1. The database contains a table called "Order" which is a SQL reserved keyword
                                2. ALWAYS use square brackets when querying the Order table: [Order]
                                3. Example CORRECT: SELECT * FROM [Order]
                                4. Example WRONG: SELECT * FROM Order (will cause syntax error)
                                5. Other tables like Customer, Product, Employee do not need brackets

                                When analyzing data:
                                - Always start by using get_schema to understand available tables
                                - Use analyze_data tool to execute SQL queries
                                - For the user, db_name, and other parameters, extract them from the user's message
                                - Be specific and thorough in your analysis
                                - If you get a syntax error with "Order", remember to use [Order]
                                - Provide clear, actionable insights"""

            agent = create_react_agent(
                model=llm,
                tools=tools,
                prompt=system_message
            )
            print("✓ Using LangGraph agent")
            return agent
            
        except ImportError:
            print("LangGraph not available, trying classic methods...")
        
        # Try classic initialize_agent as fallback
        try:
            from langchain_classic.agents import initialize_agent, AgentType
            
            agent = initialize_agent(
                tools=tools,
                llm=llm,
                agent=AgentType.ZERO_SHOT_REACT_DESCRIPTION,
                verbose=True,
                handle_parsing_errors=True,
                max_iterations=20
            )
            print("✓ Using langchain_classic agent")
            return agent
            
        except ImportError:
            pass
        
        # Try standard initialize_agent
        try:
            from langchain.agents import initialize_agent, AgentType
            
            agent = initialize_agent(
                tools=tools,
                llm=llm,
                agent=AgentType.ZERO_SHOT_REACT_DESCRIPTION,
                verbose=True,
                handle_parsing_errors=True,
                max_iterations=20
            )
            print("✓ Using langchain agent")
            return agent
            
        except ImportError:
            pass
        
        raise ImportError(
            "Could not find compatible agent creation method.\n"
            "Please install: pip install langgraph langchain-classic langchain"
        )
        
    except Exception as e:
        print(f"Error building agent: {e}")
        raise