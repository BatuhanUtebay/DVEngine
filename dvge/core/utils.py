# dvge/core/utils.py

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


def get_file_mime_type(filepath):
    """Get the MIME type based on file extension."""
    ext = os.path.splitext(filepath)[1].lower()
    
    # Image types
    if ext in ['.jpg', '.jpeg']:
        return 'image/jpeg'
    elif ext == '.png':
        return 'image/png'
    elif ext == '.gif':
        return 'image/gif'
    elif ext == '.webp':
        return 'image/webp'
    elif ext == '.svg':
        return 'image/svg+xml'
    
    # Audio types
    elif ext == '.mp3':
        return 'audio/mpeg'
    elif ext == '.wav':
        return 'audio/wav'
    elif ext == '.ogg':
        return 'audio/ogg'
    elif ext == '.m4a':
        return 'audio/mp4'
    elif ext == '.flac':
        return 'audio/flac'
    
    # Default fallbacks
    elif ext in ['.jpg', '.jpeg', '.png', '.gif', '.webp', '.bmp']:
        return 'image/png'  # Default image
    elif ext in ['.mp3', '.wav', '.ogg', '.m4a', '.flac']:
        return 'audio/mpeg'  # Default audio
    
    return 'application/octet-stream'  # Generic binary


def validate_file_size(filepath, max_size_mb=50):
    """Validate that the file size is reasonable for embedding."""
    try:
        file_size = os.path.getsize(filepath)
        size_mb = file_size / (1024 * 1024)
        
        if size_mb > max_size_mb:
            messagebox.showwarning(
                "Large File Warning", 
                f"File {os.path.basename(filepath)} is {size_mb:.1f}MB. "
                f"Large files may cause performance issues in the exported game."
            )
            return messagebox.askyesno(
                "Continue Export?", 
                "Do you want to continue with this large file?"
            )
        
        return True
        
    except Exception as e:
        print(f"Error checking file size for {filepath}: {e}")
        return True  # Allow export to continue


def get_supported_formats():
    """Get lists of supported file formats."""
    return {
        'images': ['.jpg', '.jpeg', '.png', '.gif', '.webp', '.bmp'],
        'audio': ['.mp3', '.wav', '.ogg', '.m4a', '.flac']
    }