"""
Simple script to run the dashboard
This makes it easy to start your app without remembering complex commands
"""

import sys
import os

# Add the project root to Python path so imports work
project_root = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, project_root)

# Import and run the app
from src.dashboard.app import app

if __name__ == "__main__":
    print("Starting Economics of AI Dashboard...")
    print("Open your browser to: http://localhost:8050")
    print("Press Ctrl+C to stop the server\n")
    
    app.run_server(debug=True, host="127.0.0.1", port=8050)