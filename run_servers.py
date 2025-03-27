import subprocess
import time
import os
import sys

def run_servers():
    # Get the current directory
    current_dir = os.path.dirname(os.path.abspath(__file__))
    
    print("Starting FastAPI server...")
    fastapi_process = subprocess.Popen(
        [sys.executable, "main.py"],
        cwd=current_dir
    )
    
    print("Waiting for FastAPI to start...")
    time.sleep(2)  # Give FastAPI time to start
    
    print("Starting Streamlit dashboard...")
    streamlit_process = subprocess.Popen(
        [sys.executable, "-m", "streamlit", "run", "dashboard/app.py"],
        cwd=current_dir
    )
    
    print("All servers started!")
    print("- FastAPI: http://localhost:8000")
    print("- MCP Server: http://localhost:8080")
    print("- Streamlit Dashboard: http://localhost:8501")
    
    try:
        # Keep the script running to maintain both processes
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        print("Shutting down servers...")
        fastapi_process.terminate()
        streamlit_process.terminate()
        print("Servers shut down successfully")

if __name__ == "__main__":
    run_servers()