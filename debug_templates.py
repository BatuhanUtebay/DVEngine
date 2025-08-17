#!/usr/bin/env python3
"""Debug template system issues."""

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

def debug_template_system():
    print("=== Template System Debug ===")
    
    # Test 1: Template Manager
    print("\n1. Testing Template Manager...")
    try:
        from dvge.core.template_manager import TemplateManager
        tm = TemplateManager()
        templates = tm.get_all_templates()
        print(f"   Found {len(templates)} templates")
        for template in templates:
            print(f"   - {template.name}")
    except Exception as e:
        print(f"   ERROR: {e}")
        import traceback
        traceback.print_exc()
        return
    
    # Test 2: Template Dialog Import
    print("\n2. Testing Template Dialog Import...")
    try:
        from dvge.ui.dialogs.template_selection_dialog import TemplateSelectionDialog
        print("   Template dialog imported successfully")
    except Exception as e:
        print(f"   ERROR: {e}")
        import traceback
        traceback.print_exc()
        return
    
    # Test 3: Basic CTk functionality
    print("\n3. Testing CustomTkinter...")
    try:
        import customtkinter as ctk
        # Don't actually show a window, just test creation
        app = ctk.CTk()
        print("   CustomTkinter working")
        app.destroy()  # Clean up
    except Exception as e:
        print(f"   ERROR: {e}")
        import traceback
        traceback.print_exc()
        return
        
    print("\n=== All tests passed! ===")
    print("The template system should be working.")
    print("If templates don't show in the editor, the issue might be:")
    print("1. The 'New Project' menu item isn't calling the right function")
    print("2. There's an error dialog being suppressed")
    print("3. The dialog is opening but not visible (behind other windows)")

if __name__ == "__main__":
    debug_template_system()