"""
Financial Analytics Dashboard Launcher
Easy way to start all services
"""

import subprocess
import sys
import time
import webbrowser
from threading import Thread

def start_streamlit():
    """Start Streamlit dashboard"""
    print("🚀 Starting Streamlit Dashboard...")
    subprocess.run([
        sys.executable, "-m", "streamlit", "run", 
        "src/dashboard/main_dashboard.py", 
        "--server.port", "8501"
    ])

def start_api():
    """Start FastAPI server"""
    print("🚀 Starting FastAPI Server...")
    subprocess.run([
        sys.executable, "-m", "uvicorn", 
        "src.api.main:app", 
        "--host", "localhost", 
        "--port", "8000", 
        "--reload"
    ])

def open_browser():
    """Open browser tabs"""
    time.sleep(3)  # Wait for servers to start
    print("🌐 Opening browser...")
    webbrowser.open("http://localhost:8501")  # Streamlit
    time.sleep(1)
    webbrowser.open("http://localhost:8000")  # API docs

def main():
    print("=" * 60)
    print("📈 FINANCIAL ANALYTICS DASHBOARD LAUNCHER")
    print("=" * 60)
    print("Starting all services...")
    print()
    
    choice = input("Choose option:\n1. Streamlit Dashboard only\n2. FastAPI Server only\n3. Both services\n4. Quick demo\nEnter choice (1-4): ")
    
    if choice == "1":
        print("\n🚀 Starting Streamlit Dashboard...")
        print("🌐 Will open at: http://localhost:8501")
        Thread(target=lambda: webbrowser.open("http://localhost:8501")).start()
        time.sleep(2)
        start_streamlit()
        
    elif choice == "2":
        print("\n🚀 Starting FastAPI Server...")
        print("📚 API docs at: http://localhost:8000/docs")
        Thread(target=lambda: webbrowser.open("http://localhost:8000/docs")).start()
        time.sleep(2)
        start_api()
        
    elif choice == "3":
        print("\n🚀 Starting both services...")
        print("📊 Streamlit Dashboard: http://localhost:8501")
        print("📚 FastAPI Documentation: http://localhost:8000/docs")
        
        # Start API in background
        api_process = subprocess.Popen([
            sys.executable, "-m", "uvicorn", 
            "src.api.main:app", 
            "--host", "localhost", 
            "--port", "8000"
        ])
        
        time.sleep(3)
        
        # Open browsers
        Thread(target=open_browser).start()
        
        # Start Streamlit in foreground
        try:
            start_streamlit()
        except KeyboardInterrupt:
            print("\n🛑 Shutting down services...")
            api_process.terminate()
            
    elif choice == "4":
        print("\n🎯 Running quick demo...")
        subprocess.run([sys.executable, "quick_test.py"])
        
    else:
        print("❌ Invalid choice. Please run again.")

if __name__ == "__main__":
    main()