#!/usr/bin/env python3
"""
Stock Analytics Dashboard - Run Script
"""

import sys
import os
import subprocess

def install_dependencies():
    """Install required dependencies"""
    print("Installing dependencies...")
    try:
        subprocess.check_call([sys.executable, "-m", "pip", "install", "-r", "requirements.txt"])
        print("✓ Dependencies installed successfully")
    except subprocess.CalledProcessError as e:
        print(f"✗ Error installing dependencies: {e}")
        return False
    return True

def run_server():
    """Start the FastAPI server"""
    print("\nStarting Stock Analytics Dashboard...")
    print("Dashboard will be available at: http://localhost:8000")
    print("Press Ctrl+C to stop the server\n")

    try:
        import uvicorn
        uvicorn.run(
            "main:app",
            host="0.0.0.0",
            port=8000,
            reload=True,
            log_level="info"
        )
    except KeyboardInterrupt:
        print("\n\nServer stopped.")
    except Exception as e:
        print(f"✗ Error starting server: {e}")
        return False
    return True

def main():
    # Add current directory to path
    sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

    print("=" * 60)
    print("Stock Market Trend Prediction & Financial Analytics Dashboard")
    print("=" * 60)

    if not install_dependencies():
        print("\nFailed to install dependencies. Please check the error above.")
        sys.exit(1)

    run_server()

if __name__ == "__main__":
    main()
