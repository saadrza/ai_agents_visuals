import streamlit as st
import os
import yaml
import re
import glob
import time
import logging
import sqlite3
from yaml.loader import SafeLoader
import streamlit_authenticator as stauth
from dotenv import load_dotenv
from pathlib import Path
from omegaconf import OmegaConf

# Import custom modules
from agent.orchestrator import build_agent
from data.db_registry import DATABASES, USER_DB_ACCESS

# ============================================================================
# CONFIGURATION
# ============================================================================


IMAGES_DIR = "generated_images"
IMAGE_MAX_AGE_HOURS = 1
RATE_LIMIT_SECONDS = 2

# Logging setup
logging.basicConfig(
    filename='app.log',
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# ============================================================================
# SETUP
# ============================================================================

st.set_page_config(
    page_title="Secure Data Agent",
    page_icon="🔒",
    layout="wide"
)
load_dotenv()
os.makedirs(IMAGES_DIR, exist_ok=True)

# ============================================================================
# HELPER FUNCTIONS
# ============================================================================

def load_auth_config():
    """Load authentication configuration from YAML file."""
    try:
        with open('auth.yaml') as file:
            return yaml.load(file, Loader=SafeLoader)
    except FileNotFoundError:
        st.error("❌ Configuration file 'auth.yaml' not found.")
        st.info("💡 Please create 'auth.yaml' in the root directory.")
        logger.error("auth.yaml not found")
        st.stop()
    except yaml.YAMLError as e:
        st.error(f"❌ Error parsing 'auth.yaml': {e}")
        logger.error(f"YAML parsing error: {e}")
        st.stop()


def cleanup_old_files(directory=IMAGES_DIR, extension="*.png", max_age_hours=IMAGE_MAX_AGE_HOURS):
    """Remove old generated files to prevent disk space issues."""
    pattern = os.path.join(directory, extension)
    files = glob.glob(pattern)
    current_time = time.time()
    
    for file in files:
        try:
            if current_time - os.path.getmtime(file) > (max_age_hours * 3600):
                os.remove(file)
                logger.info(f"Cleaned up old file: {file}")
        except Exception as e:
            logger.warning(f"Could not remove {file}: {e}")


def validate_database(db_path):
    """Validate that the database file exists and is accessible."""
    if not os.path.exists(db_path):
        st.error(f"❌ Database file not found: {db_path}")
        logger.error(f"Database not found: {db_path}")
        return False
    
    try:
        conn = sqlite3.connect(db_path)
        conn.execute("SELECT 1")
        conn.close()
        return True
    except sqlite3.Error as e:
        st.error(f"❌ Invalid database file: {e}")
        logger.error(f"Database validation failed: {e}")
        return False


def extract_response(response):
    """Parse output from LangChain/LangGraph agents."""
    # Handle LangGraph / OpenAI Dictionary format
    if isinstance(response, dict) and "messages" in response:
        final_message = response["messages"][-1]
        return getattr(final_message, 'content', str(final_message))
    
    # Handle Classic LangChain Dictionary
    if isinstance(response, dict):
        return response.get("output", str(response))
    
    # Handle Direct String Output
    return str(response)


def reset_chat():
    """Reset chat state and clean up resources."""
    st.session_state.messages = []
    st.session_state.agent = None
    cleanup_old_files()
    logger.info("Chat reset")


def check_rate_limit():
    """Enforce rate limiting to prevent spam."""
    if "last_query_time" not in st.session_state:
        st.session_state.last_query_time = 0
    
    current_time = time.time()
    time_since_last = current_time - st.session_state.last_query_time
    
    if time_since_last < RATE_LIMIT_SECONDS:
        st.warning("⏳ Please wait a moment before submitting another query.")
        return False
    
    st.session_state.last_query_time = current_time
    return True


def build_agent_safely(db_path):
    """Build agent with error handling."""
    try:
        agent = build_agent(
            api_key=os.getenv("OPENAI_API_KEY"),
            model="gpt-4o",
            temperature=0,
            db_path=db_path
        )
        logger.info(f"Agent built successfully for: {db_path}")
        return agent
    except Exception as e:
        st.error(f"❌ Failed to build agent: {e}")
        logger.error(f"Agent build failed: {e}")
        st.stop()


def invoke_agent_safely(agent, prompt, user_role, db_path):
    """Invoke agent with proper error handling."""
    final_prompt = (
        f"User Role: {user_role}\n"
        f"Database Path: {db_path}\n"
        f"Task: {prompt}\n"
        f"IMPORTANT: You are connected to the database. "
        f"If you create a plot, save it in the '{IMAGES_DIR}/' directory "
        f"with a unique filename (e.g., '{IMAGES_DIR}/plot_{{timestamp}}.png') "
        f"and mention the full path in your response."
    )
    
    if hasattr(agent, 'invoke'):
        try:
            return agent.invoke(
                {"messages": [("user", final_prompt)]},
                config={"recursion_limit": 50}
            )
        except (TypeError, ValueError):
            return agent.invoke({"input": final_prompt})
    else:
        return agent(final_prompt)


def handle_image_display(final_answer):
    """Detect and display generated images from agent response."""
    image_match = re.search(rf"{IMAGES_DIR}/[\w-]+\.png", final_answer)
    
    if image_match:
        img_path = os.path.normpath(image_match.group(0))
        
        # Security: ensure path is within IMAGES_DIR
        if img_path.startswith(IMAGES_DIR) and os.path.exists(img_path):
            st.image(img_path, caption="Generated Visualization")
            
            # Add download button
            with open(img_path, "rb") as file:
                st.download_button(
                    label="📥 Download Image",
                    data=file,
                    file_name=os.path.basename(img_path),
                    mime="image/png",
                    key=f"download_{os.path.basename(img_path)}"
                )
            
            # Save to chat history
            st.session_state.messages.append({
                "role": "assistant",
                "image": img_path
            })
            
            logger.info(f"Image displayed: {img_path}")

# ============================================================================
# AUTHENTICATION
# ============================================================================

config = load_auth_config()

authenticator = stauth.Authenticate(
    config['credentials'],
    config['cookie']['name'],
    config['cookie']['key'],
    config['cookie']['expiry_days']
)

authenticator.login()

# ============================================================================
# MAIN APPLICATION
# ============================================================================

if st.session_state["authentication_status"] is False:
    st.error("❌ Username/password is incorrect")
    logger.warning("Failed login attempt")

elif st.session_state["authentication_status"] is None:
    st.warning("🔐 Please enter your username and password")

elif st.session_state["authentication_status"]:
    # User authenticated - start main app
    
    # Get user information
    username = st.session_state["username"]
    user_real_name = st.session_state["name"]
    user_role = config['credentials']['usernames'][username].get('role', 'guest')
    
    logger.info(f"User logged in: {username} ({user_role})")
    
    # ========================================================================
    # SIDEBAR
    # ========================================================================
    
    with st.sidebar:
        # User info
        st.write(f"👤 **{user_real_name}**")
        st.caption(f"Role: {user_role.upper()}")
        
        # Logout button
        authenticator.logout('Logout', 'sidebar')
        st.divider()
        
        # Database selection
        allowed_db_names = USER_DB_ACCESS.get(user_role, [])
        available_dbs = {
            name: path 
            for name, path in DATABASES.items() 
            if name in allowed_db_names
        }
        
        if not available_dbs:
            st.error("⛔ You do not have access to any databases.")
            logger.warning(f"User {username} has no database access")
            st.stop()
        
        selected_db_name = st.selectbox(
            "Select Database",
            options=list(available_dbs.keys()),
            on_change=reset_chat
        )
        db_path = available_dbs[selected_db_name]
        
        st.divider()
        
        # Tips section
        st.markdown("### 💡 Tips")
        st.caption("• Ask for specific tables or schemas")
        st.caption("• Request visualizations (e.g., 'Plot sales trends')")
        st.caption("• Use natural language queries")
    
    # ========================================================================
    # MAIN CHAT INTERFACE
    # ========================================================================
    
    st.title(f"📊 {selected_db_name} Analyst")
    
    # Initialize session state
    if "messages" not in st.session_state:
        st.session_state.messages = []
    if "agent" not in st.session_state:
        st.session_state.agent = None
    
    # Build agent (lazy loading)
    if st.session_state.agent is None:
        cleanup_old_files()
        
        if validate_database(db_path):
            with st.spinner("🔌 Connecting to database..."):
                st.session_state.agent = build_agent_safely(db_path)
                
                # Welcome message
                st.session_state.messages.append({
                    "role": "assistant",
                    "content": (
                        f"Hello **{user_real_name}**! 👋\n\n"
                        f"I'm connected to the **{selected_db_name}** database. "
                        f"How can I help you analyze your data today?"
                    )
                })
                logger.info(f"Agent initialized for {username} on {selected_db_name}")
    
    # Display chat history
    for msg in st.session_state.messages:
        with st.chat_message(msg["role"]):
            if "content" in msg:
                st.markdown(msg["content"])
            if "image" in msg:
                if os.path.exists(msg["image"]):
                    st.image(msg["image"])
                    
                    # Add download button for historical images
                    with open(msg["image"], "rb") as file:
                        st.download_button(
                            label="📥 Download",
                            data=file,
                            file_name=os.path.basename(msg["image"]),
                            mime="image/png",
                            key=f"hist_{os.path.basename(msg['image'])}"
                        )
    
    # Handle user input
    if prompt := st.chat_input("Ask a question about your data..."):
        # Rate limiting
        if not check_rate_limit():
            st.stop()
        
        # Add user message to history
        st.session_state.messages.append({"role": "user", "content": prompt})
        
        with st.chat_message("user"):
            st.markdown(prompt)
        
        logger.info(f"User query: {username} - {prompt}")
        
        # Generate response
        with st.chat_message("assistant"):
            message_placeholder = st.empty()
            
            with st.spinner("🤔 Analyzing data..."):
                try:
                    # Invoke agent
                    raw_response = invoke_agent_safely(
                        st.session_state.agent,
                        prompt,
                        user_role,
                        db_path
                    )
                    
                    # Process response
                    final_answer = extract_response(raw_response)
                    message_placeholder.markdown(final_answer)
                    
                    # Save to history
                    st.session_state.messages.append({
                        "role": "assistant",
                        "content": final_answer
                    })
                    
                    # Handle image display
                    handle_image_display(final_answer)
                    
                    logger.info(f"Response generated for: {username}")
                
                except Exception as e:
                    error_msg = f"❌ An error occurred: {str(e)}"
                    st.error(error_msg)
                    logger.error(f"Query error for {username}: {e}", exc_info=True)