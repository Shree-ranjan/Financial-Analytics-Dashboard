"""
Script to help capture screenshots for the Financial Analytics Dashboard README
"""

import webbrowser
import os
import time

def open_dashboard():
    """Open the dashboard in the default browser"""
    print("Opening Financial Analytics Dashboard...")
    webbrowser.open("http://localhost:8501")
    print("Dashboard opened in your browser!")
    print("\nPlease follow these steps to capture screenshots:")
    print("1. Wait for the dashboard to load completely")
    print("2. Capture the following views:")
    print("   - Main dashboard overview")
    print("   - Candlestick chart with indicators")
    print("   - Portfolio analysis section")
    print("   - Trading signals section")
    print("3. Save screenshots in the 'screenshots' directory with these names:")
    print("   - dashboard_overview.png")
    print("   - candlestick_chart.png")
    print("   - portfolio_analysis.png")
    print("   - trading_signals.png")
    print("\nOnce you've captured all screenshots, update the README.md file.")

def create_screenshots_dir():
    """Create screenshots directory if it doesn't exist"""
    if not os.path.exists("screenshots"):
        os.makedirs("screenshots")
        print("Created 'screenshots' directory")
    else:
        print("'screenshots' directory already exists")

if __name__ == "__main__":
    create_screenshots_dir()
    print("To capture screenshots:")
    print("1. First, make sure the dashboard is running:")
    print("   python -m streamlit run src/dashboard/main_dashboard.py")
    print("2. Then run this script to open the dashboard in your browser:")
    print("   python capture_screenshots.py")
    input("\nPress Enter to open the dashboard in your browser...")
    open_dashboard()