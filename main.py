# main.py

"""
The main entry point for the Dialogue Venture Game Engine.
"""

import sys
import os

# Add the project root to the Python path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

# Import DVGApp (original version)
from dvge import DVGApp


def main():
    """
    The main entry point for the Dialogue Venture Game Engine.
    """
    print("*** Starting Dialogue Venture Game Engine ***")
    print("=" * 50)
    
    try:
        app = DVGApp()
        
        print("=" * 50)
        print("*** DVGE Ready! Happy storytelling! ***")
        print("=" * 50)
        
        # Start the application
        app.mainloop()
        
    except KeyboardInterrupt:
        print("\n* DVGE shutdown requested by user")
    except Exception as e:
        print(f"! Error starting application: {e}")
        print("\n* Debug information:")
        import traceback
        traceback.print_exc()
    
    finally:
        print("\n* Thank you for using DVGE!")


if __name__ == "__main__":
    main()