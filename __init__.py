"""
Blender AI Procedural Material Generator
Main addon file - Entry point dan registrasi
"""

bl_info = {
    "name": "AI Procedural Material Generator",
    "author": "Hafizh Zaldy Alviansyah",
    "version": (1, 0, 0),
    "blender": (3, 6, 0),
    "location": "Shader Editor > Sidebar > AI Material",
    "description": "Generate procedural shader materials using AI (Google Gemini) from natural language prompts",
    "warning": "Requires internet connection and Google Gemini API key",
    "wiki_url": "",
    "category": "Material",
}


import bpy
import sys
import os


# Add addon directory to Python path untuk imports
addon_dir = os.path.dirname(__file__)
if addon_dir not in sys.path:
    sys.path.append(addon_dir)


# Import modules
from . import operators
from . import panels
from . import ai_connector
from . import material_generator
from . import utils
from . import prompt_templates
from . import node_reference
from . import material_schema


# Module list untuk reload (development)
modules = [
    operators,
    panels,
    ai_connector,
    material_generator,
    utils,
    prompt_templates,
    node_reference,
    material_schema,
]


def register():
    """Register addon classes dan initialize"""
    print("=" * 50)
    print("AI Procedural Material Generator - Registering")
    print("=" * 50)
    
    # Check dependencies
    try:
        from google import genai
        print("✓ google-genai found")
    except ImportError:
        print("⚠ WARNING: google-genai not found!")
        print("Please run install_dependencies.bat to install required packages")
    
    try:
        import requests
        print("✓ requests found")
    except ImportError:
        print("⚠ WARNING: requests not found!")
        print("Please run install_dependencies.bat to install required packages")
    
    # Register modules
    operators.register()
    panels.register()
    
    print("✓ AI Material Generator registered successfully")
    print("Location: Shader Editor > Sidebar > AI Material tab")
    print("=" * 50)


def unregister():
    """Unregister addon classes"""
    print("AI Procedural Material Generator - Unregistering")
    
    # Unregister modules
    panels.unregister()
    operators.unregister()
    
    print("✓ AI Material Generator unregistered")


# Untuk development - reload modules
if "bpy" in locals():
    import importlib
    for module in modules:
        importlib.reload(module)


if __name__ == "__main__":
    register()
