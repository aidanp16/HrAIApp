"""
Streamlit UI for HR Hiring Assistant
Main user interface for the agentic AI application
"""

import streamlit as st
from typing import Dict, Any
import sys
import os

# Add src to path for imports
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))

from agent.hiring_agent import HiringAgent
from database.db_manager import DatabaseManager

def main():
    """Main Streamlit application"""
    st.set_page_config(
        page_title="HR Hiring Assistant",
        page_icon="👥",
        layout="wide"
    )
    
    st.title("🤖 HR Hiring Assistant")
    st.subtitle("AI-Powered Startup Hiring Planner")
    
    # TODO: Implement chat interface
    # TODO: Add conversation history
    # TODO: Add export functionality
    # TODO: Add professional styling
    
    # Placeholder for now
    st.info("🚧 Under Development - Coming Soon!")
    
    with st.sidebar:
        st.header("Session Info")
        st.info("Session management will be implemented here")
        
        st.header("Export Options")
        st.info("Export functionality coming soon")

if __name__ == "__main__":
    main()
