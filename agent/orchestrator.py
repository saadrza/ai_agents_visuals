# agent/orchestrator.py
from langchain_openai import ChatOpenAI
from langchain.agents import create_agent
from langchain_classic.agents import AgentExecutor
from langchain_classic import hub

from tools.analysis_tool import DataAnalysisTool
from tools.schema_tool import SchemaTool
from tools.visualization_tool import VisualizationTool


def build_agent(api_key: str = None, temperature: float = 0) -> AgentExecutor:
    """
    Build and return a LangChain agent executor with data analysis tools.
    
    Args:
        api_key: OpenAI API key (optional, can use env var)
        temperature: LLM temperature for response randomness
        
    Returns:
        Configured AgentExecutor instance
        
    Raises:
        ValueError: If tools fail to initialize
        Exception: If agent creation fails
    """
    try:
        # --- Initialize Tools ---
        tools = [
            SchemaTool(),
            DataAnalysisTool(),
            VisualizationTool(),
        ]
        
        # Validate tools
        if not all(tools):
            raise ValueError("One or more tools failed to initialize")

        # --- Initialize LLM ---
        llm = ChatOpenAI(
            model="gpt-4o",
            temperature=temperature,
            api_key=api_key
        )

        # --- Load Prompt Template ---
        prompt = hub.pull("hwchase17/react")

        # --- Create Agent ---
        agent = create_agent(
            model=llm,
            tools=tools,
            #prompt=prompt  # Pass prompt directly, not as string
        )

        # --- Create Executor ---
        agent_executor = AgentExecutor(
            agent=agent,
            tools=tools,
            verbose=True,
            handle_parsing_errors=True,  # Graceful error handling
            max_iterations=15  # Prevent infinite loops
        )
        
        return agent_executor
        
    except Exception as e:
        print(f"Error building agent: {e}")
        raise