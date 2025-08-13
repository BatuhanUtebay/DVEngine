# main.py

"""
The main entry point for the Dialogue Venture Game Engine.
"""

import sys
import os

# Add the project root to the Python path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from dvge import DVGApp


def main():
    """
    The main entry point for the Dialogue Venture Game Engine.
    """
    try:
        app = DVGApp()
        app.mainloop()
    except Exception as e:
        print(f"Error starting application: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    main()