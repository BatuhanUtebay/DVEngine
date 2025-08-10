# dvge/utils.py
"""Utility functions for the DVGE application."""

import os
import base64
from tkinter import messagebox

def encode_file_to_base64(filepath, file_type="image"):
    """Encode a file to base64 data URI."""
    if not filepath or not os.path.exists(filepath):
        return ""
    
    try:
        with open(filepath, "rb") as file:
            encoded_string = base64.b64encode(file.read()).decode('utf-8')
            
            if file_type == "image":
                return f"data:image/png;base64,{encoded_string}"
            elif file_type == "audio":
                return f"data:audio/mpeg;base64,{encoded_string}"
            else:
                return encoded_string
                
    except Exception as e:
        print(f"Could not encode file {filepath}: {e}")
        return ""

def validate_node_id(node_id, existing_nodes, exclude_id=None):
    """Validate a node ID."""
    if not node_id or not node_id.strip():
        return False, "Node ID cannot be empty."
    
    node_id = node_id.strip()
    
    if exclude_id and node_id == exclude_id:
        return True, ""
    
    if node_id in existing_nodes:
        return False, f"Node ID '{node_id}' already exists."
    
    # Check for invalid characters
    invalid_chars = ['/', '\\', ':', '*', '?', '"', '<', '>', '|']
    for char in invalid_chars:
        if char in node_id:
            return False, f"Node ID cannot contain '{char}'."
    
    return True, ""

def safe_float_conversion(value, default=0.0):
    """Safely convert a value to float."""
    try:
        return float(value)
    except (ValueError, TypeError):
        return default

def safe_int_conversion(value, default=0):
    """Safely convert a value to int."""
    try:
        return int(value)
    except (ValueError, TypeError):
        return default

def show_error(title, message):
    """Show an error message dialog."""
    messagebox.showerror(title, message)

def show_warning(title, message):
    """Show a warning message dialog."""
    messagebox.showwarning(title, message)

def show_info(title, message):
    """Show an info message dialog."""
    messagebox.showinfo(title, message)

def ask_yes_no(title, message):
    """Show a yes/no question dialog."""
    return messagebox.askyesno(title, message)