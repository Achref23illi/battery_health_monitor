import sys
import os

# Add the project root directory to the Python path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from src.gui import run_app

def main():
    """Main function to run the application"""
    run_app()

if __name__ == "__main__":
    main()