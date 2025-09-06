#!/usr/bin/env python3
"""
Streamlit App Launcher for HR Hiring Assistant
Handles proper imports and runs the Streamlit application
"""

import sys
import os
import subprocess

# Add project root to Python path
project_root = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, project_root)

def main():
    """Launch the Streamlit application"""
    app_path = os.path.join(project_root, "src", "ui", "streamlit_app.py")
    
    # Run streamlit with proper configuration
    cmd = [
        sys.executable, "-m", "streamlit", "run", app_path,
        "--server.port", "8501",
        "--server.headless", "true",
        "--browser.gatherUsageStats", "false"
    ]
    
    print("🚀 Starting HR Hiring Assistant...")
    print("📍 URL: http://localhost:8501")
    print("⏹️  Press Ctrl+C to stop")
    print("=" * 50)
    
    try:
        subprocess.run(cmd)
    except KeyboardInterrupt:
        print("\n👋 HR Hiring Assistant stopped")

if __name__ == "__main__":
    main()
