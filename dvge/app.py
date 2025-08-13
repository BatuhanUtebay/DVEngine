# dvge/app.py

"""
Main application entry point for DVGE.
This file serves as the primary import for the application.
"""

from .core.application import DVGApp

# Re-export the main app class for backwards compatibility
__all__ = ['DVGApp']