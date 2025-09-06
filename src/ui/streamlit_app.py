"""
Streamlit UI for HR Hiring Assistant
Professional interface for the agentic AI application
"""

import streamlit as st
from typing import Dict, Any, List
import sys
import os
import json
import re
from datetime import datetime
import base64

# Add project root to path for proper imports
project_root = os.path.dirname(os.path.dirname(os.path.dirname(__file__)))
if project_root not in sys.path:
    sys.path.insert(0, project_root)

# Import the hiring agent
try:
    from src.agent.hiring_agent import HiringAgent
except ImportError:
    # Fallback for different execution contexts
    sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))
    from agent.hiring_agent import HiringAgent

# Page configuration
st.set_page_config(
    page_title="HR Hiring Assistant",
    page_icon="👥",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS for professional styling
st.markdown("""
<style>
    .main-header {
        text-align: center;
        padding: 1rem 0;
        margin-bottom: 2rem;
        border-bottom: 2px solid #f0f2f6;
    }
    
    .chat-message {
        padding: 1rem;
        border-radius: 10px;
        margin: 1rem 0;
    }
    
    .user-message {
        background-color: #e3f2fd;
        border-left: 4px solid #2196f3;
    }
    
    .assistant-message {
        background-color: #f3e5f5;
        border-left: 4px solid #9c27b0;
    }
    
    .document-section {
        background-color: #fafafa;
        border: 1px solid #e0e0e0;
        border-radius: 8px;
        padding: 1rem;
        margin: 0.5rem 0;
    }
    
    .document-header {
        color: #1976d2;
        font-weight: bold;
        margin-bottom: 0.5rem;
        border-bottom: 1px solid #e0e0e0;
        padding-bottom: 0.25rem;
    }
    
    .success-indicator {
        color: #2e7d32;
        font-weight: bold;
    }
    
    .warning-indicator {
        color: #f57c00;
        font-weight: bold;
    }
    
    .metric-card {
        background: linear-gradient(45deg, #2196f3, #21cbf3);
        color: white;
        padding: 1rem;
        border-radius: 10px;
        text-align: center;
        margin: 0.5rem;
    }
    
    .stButton > button {
        background-color: #1976d2;
        color: white;
        border: none;
        border-radius: 5px;
        padding: 0.5rem 1rem;
        font-weight: bold;
    }
    
    .stButton > button:hover {
        background-color: #1565c0;
        border: none;
    }
</style>
""", unsafe_allow_html=True)

def init_session_state():
    """Initialize session state variables"""
    if 'messages' not in st.session_state:
        st.session_state.messages = []
    if 'agent' not in st.session_state:
        st.session_state.agent = HiringAgent()
    if 'current_result' not in st.session_state:
        st.session_state.current_result = None
    if 'session_id' not in st.session_state:
        st.session_state.session_id = datetime.now().strftime("%Y%m%d_%H%M%S")

def display_message(role: str, content: str, timestamp: str = None):
    """Display a chat message with proper styling"""
    if timestamp is None:
        timestamp = datetime.now().strftime("%H:%M:%S")
    
    if role == "user":
        st.markdown(f"""
        <div class="chat-message user-message">
            <strong>👤 You</strong> <small>({timestamp})</small><br>
            {content}
        </div>
        """, unsafe_allow_html=True)
    else:
        st.markdown(f"""
        <div class="chat-message assistant-message">
            <strong>🤖 HR Assistant</strong> <small>({timestamp})</small><br>
            {content}
        </div>
        """, unsafe_allow_html=True)

def format_document_section(title: str, content: str, icon: str = "📄") -> str:
    """Format a document section with proper styling"""
    # Clean up markdown formatting for HTML display
    content_html = content.replace("\n", "<br>")
    content_html = re.sub(r'\*\*(.*?)\*\*', r'<strong>\1</strong>', content_html)
    content_html = re.sub(r'\*(.*?)\*', r'<em>\1</em>', content_html)
    content_html = re.sub(r'- (.*?)<br>', r'• \1<br>', content_html)
    
    return f"""
    <div class="document-section">
        <div class="document-header">{icon} {title}</div>
        <div>{content_html}</div>
    </div>
    """

def parse_agent_response(response: str) -> Dict[str, str]:
    """Parse the agent response to extract different sections"""
    sections = {}
    
    # Define section patterns
    section_patterns = {
        "job_description": r"# Job Description[\s\S]*?(?=\n# |$)",
        "hiring_checklist": r"# Comprehensive Hiring Checklist[\s\S]*?(?=\n# |$)",
        "salary_benchmarking": r"# Salary Benchmarking & Market Intelligence[\s\S]*?(?=\n# |$)",
        "timeline": r"# Hiring Timeline[\s\S]*?(?=\n# |$)",
        "interview_questions": r"# Interview Questions[\s\S]*?(?=\n# |$)",
        "recommendations": r"# Strategic Recommendations[\s\S]*?(?=\n# |$)"
    }
    
    for section_name, pattern in section_patterns.items():
        match = re.search(pattern, response, re.MULTILINE | re.IGNORECASE)
        if match:
            sections[section_name] = match.group().strip()
    
    return sections

def display_hiring_package(result: Dict[str, Any]):
    """Display the comprehensive hiring package in an organized way"""
    if not result or not result.get('success'):
        st.error("❌ Failed to generate hiring package")
        return
    
    # Display success metrics
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.markdown(f"""
        <div class="metric-card">
            <h4>🎯 Role Type</h4>
            <p>{result['state']['role_type'].title()}</p>
        </div>
        """, unsafe_allow_html=True)
    
    with col2:
        st.markdown(f"""
        <div class="metric-card">
            <h4>🏢 Company Stage</h4>
            <p>{result['state']['company_stage'].replace('_', ' ').title()}</p>
        </div>
        """, unsafe_allow_html=True)
    
    with col3:
        st.markdown(f"""
        <div class="metric-card">
            <h4>📊 Specificity Score</h4>
            <p>{result['state']['specificity_score']:.2f}</p>
        </div>
        """, unsafe_allow_html=True)
    
    with col4:
        questions_count = len(result['state'].get('questions_remaining', []))
        st.markdown(f"""
        <div class="metric-card">
            <h4>❓ Questions Generated</h4>
            <p>{questions_count}</p>
        </div>
        """, unsafe_allow_html=True)
    
    st.markdown("---")
    
    # Parse and display the comprehensive response
    if 'response' in result and result['response']:
        sections = parse_agent_response(result['response'])
        
        # Create tabs for different sections
        tab_names = []
        tab_contents = []
        
        if 'job_description' in sections:
            tab_names.append("📋 Job Description")
            tab_contents.append(sections['job_description'])
        
        if 'hiring_checklist' in sections:
            tab_names.append("✅ Hiring Checklist")
            tab_contents.append(sections['hiring_checklist'])
        
        if 'salary_benchmarking' in sections:
            tab_names.append("💰 Salary & Market Intelligence")
            tab_contents.append(sections['salary_benchmarking'])
        
        if 'timeline' in sections:
            tab_names.append("⏰ Timeline")
            tab_contents.append(sections['timeline'])
        
        if 'interview_questions' in sections:
            tab_names.append("🎤 Interview Questions")
            tab_contents.append(sections['interview_questions'])
        
        if 'recommendations' in sections:
            tab_names.append("💡 Recommendations")
            tab_contents.append(sections['recommendations'])
        
        if tab_names:
            tabs = st.tabs(tab_names)
            
            for i, (tab, content) in enumerate(zip(tabs, tab_contents)):
                with tab:
                    st.markdown(content)
        else:
            # Fallback: display raw response
            st.markdown("### 📄 Complete Hiring Package")
            st.markdown(result['response'])
    
    # Display questions if any were generated
    if result['state'].get('questions_remaining'):
        st.markdown("---")
        st.markdown("### ❓ **Questions for Better Context**")
        st.info("The assistant generated these questions to help create a more targeted hiring plan:")
        
        for i, question_data in enumerate(result['state']['questions_remaining'][:5], 1):
            question = question_data['question'] if isinstance(question_data, dict) else question_data
            st.markdown(f"**{i}.** {question}")

def create_download_link(content: str, filename: str, button_text: str):
    """Create a download link for content"""
    b64 = base64.b64encode(content.encode()).decode()
    href = f'<a href="data:text/markdown;base64,{b64}" download="{filename}" style="text-decoration: none;"><button style="background-color: #1976d2; color: white; border: none; padding: 8px 16px; border-radius: 4px; cursor: pointer;">{button_text}</button></a>'
    return href

def main():
    """Main Streamlit application"""
    init_session_state()
    
    # Header
    st.markdown("""
    <div class="main-header">
        <h1>🤖 HR Hiring Assistant</h1>
        <p style="font-size: 1.2em; color: #666;">AI-Powered Startup Hiring Planner with LangGraph Intelligence</p>
    </div>
    """, unsafe_allow_html=True)
    
    # Sidebar
    with st.sidebar:
        st.markdown("### 📊 Session Information")
        st.info(f"**Session ID:** {st.session_state.session_id}")
        st.info(f"**Messages:** {len(st.session_state.messages)}")
        
        st.markdown("### 🎯 How to Use")
        st.markdown("""
        1. **Describe your hiring need** - Be as specific or general as you like
        2. **Review the analysis** - See role detection and context analysis
        3. **Get your hiring package** - Job description, checklist, timeline, and more
        4. **Export results** - Download your hiring documents
        
        **Example requests:**
        - "I need to hire a senior backend engineer"
        - "Looking for a VP of Engineering for our Series A startup"
        - "Help me hire a marketing manager, budget $90k"
        """)
        
        st.markdown("### 🎨 Features")
        st.success("✅ Intelligent Role Detection")
        st.success("✅ Context-Aware Questions")
        st.success("✅ Comprehensive Job Descriptions")
        st.success("✅ Hiring Checklists & Timelines")
        st.success("✅ Salary Benchmarking")
        st.success("✅ Interview Questions")
        
        if st.button("🗑️ Clear Conversation", use_container_width=True):
            st.session_state.messages = []
            st.session_state.current_result = None
            st.rerun()
    
    # Main chat interface
    st.markdown("### 💬 Conversation")
    
    # Display chat history
    for message in st.session_state.messages:
        display_message(message['role'], message['content'], message.get('timestamp'))
    
    # Chat input
    user_input = st.chat_input("Describe your hiring need... (e.g., 'I need to hire a senior backend engineer for my startup')")
    
    if user_input:
        # Add user message to history
        timestamp = datetime.now().strftime("%H:%M:%S")
        st.session_state.messages.append({
            'role': 'user',
            'content': user_input,
            'timestamp': timestamp
        })
        
        # Display user message
        display_message('user', user_input, timestamp)
        
        # Show processing indicator
        with st.spinner('🤖 Analyzing your request and generating comprehensive hiring package...'):
            try:
                # Process with agent
                result = st.session_state.agent.process_hiring_request(user_input)
                st.session_state.current_result = result
                
                # Add assistant response to history
                assistant_response = "✅ **Analysis Complete!** I've generated a comprehensive hiring package for you. Check the details below."
                st.session_state.messages.append({
                    'role': 'assistant',
                    'content': assistant_response,
                    'timestamp': datetime.now().strftime("%H:%M:%S")
                })
                
                # Display assistant message
                display_message('assistant', assistant_response)
                
            except Exception as e:
                error_msg = f"❌ **Error:** {str(e)}"
                st.session_state.messages.append({
                    'role': 'assistant',
                    'content': error_msg,
                    'timestamp': datetime.now().strftime("%H:%M:%S")
                })
                display_message('assistant', error_msg)
        
        st.rerun()
    
    # Display current result if available
    if st.session_state.current_result:
        st.markdown("---")
        st.markdown("### 📋 **Your Comprehensive Hiring Package**")
        display_hiring_package(st.session_state.current_result)
        
        # Export options
        if st.session_state.current_result.get('response'):
            st.markdown("---")
            st.markdown("### 📥 **Export Options**")
            
            col1, col2, col3 = st.columns(3)
            
            with col1:
                if st.button("📄 Download Markdown", use_container_width=True):
                    filename = f"hiring_package_{st.session_state.session_id}.md"
                    st.download_button(
                        label="📄 Download Markdown File",
                        data=st.session_state.current_result['response'],
                        file_name=filename,
                        mime="text/markdown",
                        use_container_width=True
                    )
            
            with col2:
                if st.button("📊 Download JSON Data", use_container_width=True):
                    filename = f"hiring_data_{st.session_state.session_id}.json"
                    json_data = json.dumps(st.session_state.current_result, indent=2)
                    st.download_button(
                        label="📊 Download JSON File",
                        data=json_data,
                        file_name=filename,
                        mime="application/json",
                        use_container_width=True
                    )
            
            with col3:
                if st.button("📋 Copy to Clipboard", use_container_width=True):
                    st.code(st.session_state.current_result['response'], language='markdown')
    
    # Footer
    st.markdown("---")
    st.markdown("""
    <div style="text-align: center; color: #666; padding: 1rem;">
        <p>🚀 Powered by <strong>LangGraph</strong> & <strong>OpenAI GPT-4</strong> | 
        Built for the <strong>GenAI Builder-in-Residence Challenge</strong></p>
    </div>
    """, unsafe_allow_html=True)

if __name__ == "__main__":
    main()
