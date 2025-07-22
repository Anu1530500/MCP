import streamlit as str
from utils import run_agent_sync

str.set_page_config(page_title="MCP POC", page_icon="🤖", layout="wide")

str.title("Model Context Protocol(MCP) - Learning Path Generator")

# Initialize session state for progress
if 'current_step' not in str.session_state:
    str.session_state.current_step = ""
if 'progress' not in str.session_state:
    str.session_state.progress = 0
if 'last_section' not in str.session_state:
    str.session_state.last_section = ""
if 'is_generating' not in str.session_state:
    str.session_state.is_generating = False

# Sidebar for API and URL configuration
str.sidebar.header("Configuration")

# API Key input
google_api_key = str.sidebar.text_input("Google API Key", type="password")

# Pipedream URLs
str.sidebar.subheader("Pipedream URLs")
youtube_pipedream_url = str.sidebar.text_input("YouTube URL (Required)", 
    placeholder="Enter your Pipedream YouTube URL")

# Secondary tool selection
secondary_tool = str.sidebar.radio(
    "Select Secondary Tool:",
    ["Drive", "Notion"]
)

# Secondary tool URL input
if secondary_tool == "Drive":
    drive_pipedream_url = str.sidebar.text_input("Drive URL", 
        placeholder="Enter your Pipedream Drive URL")
    notion_pipedream_url = None
else:
    notion_pipedream_url = str.sidebar.text_input("Notion URL", 
        placeholder="Enter your Pipedream Notion URL")
    drive_pipedream_url = None

# Quick guide before goal input
str.info("""
**Quick Guide:**
1. Enter your Google API key and YouTube URL (required)
2. Select and configure your secondary tool (Drive or Notion)
3. Enter a clear learning goal, for example:
    - "I want to learn python basics in 3 days"
    - "I want to learn data science basics in 10 days"
""")

# Main content area
str.header("Enter Your Goal")
user_goal = str.text_input("Enter your learning goal:",
                        help="Describe what you want to learn, and we'll generate a structured path using YouTube content and your selected tool.")

# Progress area
progress_container = str.container()
progress_bar = str.empty()

def update_progress(message: str):
    """Update progress in the Streamlit UI"""
    str.session_state.current_step = message
    
    # Determine section and update progress
    if "Setting up agent with tools" in message:
        section = "Setup"
        str.session_state.progress = 0.1
    elif "Added Google Drive integration" in message or "Added Notion integration" in message:
        section = "Integration"
        str.session_state.progress = 0.2
    elif "Creating AI agent" in message:
        section = "Setup"
        str.session_state.progress = 0.3
    elif "Generating your learning path" in message:
        section = "Generation"
        str.session_state.progress = 0.5
    elif "Learning path generation complete" in message:
        section = "Complete"
        str.session_state.progress = 1.0
        str.session_state.is_generating = False
    else:
        section = str.session_state.last_section or "Progress"
    
    str.session_state.last_section = section
    
    # Show progress bar
    progress_bar.progress(str.session_state.progress)
    
    # Update progress container with current status
    with progress_container:
        # Show section header if it changed
        if section != str.session_state.last_section and section != "Complete":
            str.write(f"**{section}**")
        
        # Show message with tick for completed steps
        if message == "Learning path generation complete!":
            str.success("All steps completed! 🎉")
        else:
            prefix = "✓" if str.session_state.progress >= 0.5 else "→"
            str.write(f"{prefix} {message}")

# Generate Learning Path button
if str.button("Generate Learning Path", type="primary", disabled=str.session_state.is_generating):
    if not google_api_key:
        str.error("Please enter your Google API key in the sidebar.")
    elif not youtube_pipedream_url:
        str.error("YouTube URL is required. Please enter your Pipedream YouTube URL in the sidebar.")
    elif (secondary_tool == "Drive" and not drive_pipedream_url) or (secondary_tool == "Notion" and not notion_pipedream_url):
        str.error(f"Please enter your Pipedream {secondary_tool} URL in the sidebar.")
    elif not user_goal:
        str.warning("Please enter your learning goal.")
    else:
        try:
            # Set generating flag
            str.session_state.is_generating = True
            
            # Reset progress
            str.session_state.current_step = ""
            str.session_state.progress = 0
            str.session_state.last_section = ""
            
            result = run_agent_sync(
                google_api_key=google_api_key,
                youtube_pipedream_url=youtube_pipedream_url,
                drive_pipedream_url=drive_pipedream_url,
                notion_pipedream_url=notion_pipedream_url,
                user_goal=user_goal,
                progress_callback=update_progress
            )
            
            # Display results
            str.header("Your Learning Path")
            # print(result)
            if result and "messages" in result:
                for msg in result["messages"]:
                    str.markdown(f"📚 {msg.content}")

            else:
                str.error("No results were generated. Please try again.")
                str.session_state.is_generating = False
        except Exception as e:
            str.error(f"An error occurred: {str(e)}")
            str.error("Please check your API keys and URLs, and try again.")
            str.session_state.is_generating = False
