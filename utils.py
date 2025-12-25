"""
Blender AI Procedural Material Generator
Utility functions dan helper modules
"""

import bpy
import re


def validate_api_key(key):
    """
    Validate format API key Google Gemini
    
    Args:
        key (str): API key to validate
        
    Returns:
        bool: True if valid format, False otherwise
    """
    if not key or len(key) < 20:
        return False
    # Gemini API key biasanya format: AIzaSy...
    if not key.startswith('AIza'):
        return False
    return True


def get_active_material_config():
    """
    Export current active material to JSON-compatible dict
    
    Returns:
        dict: Material configuration atau None jika tidak ada material
    """
    obj = bpy.context.active_object
    if not obj or not obj.active_material:
        return None
    
    material = obj.active_material
    if not material.use_nodes:
        return None
    
    config = {
        "material_name": material.name,
        "nodes": [],
        "links": []
    }
    
    node_tree = material.node_tree
    nodes = node_tree.nodes
    
    # Export nodes
    for i, node in enumerate(nodes):
        node_data = {
            "index": i,
            "type": node.bl_idname,
            "name": node.name,
            "location": list(node.location)
        }
        
        # Export input values
        inputs = {}
        for input_socket in node.inputs:
            if hasattr(input_socket, 'default_value'):
                try:
                    # Handle different value types
                    val = input_socket.default_value
                    if hasattr(val, '__iter__') and not isinstance(val, str):
                        inputs[input_socket.name] = list(val)
                    else:
                        inputs[input_socket.name] = val
                except:
                    pass
        
        node_data["inputs"] = inputs
        config["nodes"].append(node_data)
    
    # Export links
    for link in node_tree.links:
        from_node_idx = None
        to_node_idx = None
        
        for i, node in enumerate(nodes):
            if node == link.from_node:
                from_node_idx = i
            if node == link.to_node:
                to_node_idx = i
        
        if from_node_idx is not None and to_node_idx is not None:
            config["links"].append({
                "from_node": from_node_idx,
                "from_socket": link.from_socket.name,
                "to_node": to_node_idx,
                "to_socket": link.to_socket.name
            })
    
    return config


def log_error(message, context=None):
    """
    Log error message ke console dan show di UI
    
    Args:
        message (str): Error message
        context: Blender context (optional)
    """
    print(f"[AI Material Generator ERROR] {message}")
    
    if context:
        # Show error di UI
        def draw_error(self, context):
            self.layout.label(text=message)
        
        bpy.context.window_manager.popup_menu(draw_error, title="Error", icon='ERROR')


def check_internet_connection():
    """
    Verify internet connection untuk API calls
    
    Returns:
        bool: True if connected, False otherwise
    """
    try:
        import urllib.request
        urllib.request.urlopen('https://www.google.com', timeout=3)
        return True
    except:
        return False


def sanitize_material_name(name):
    """
    Sanitize material name untuk remove invalid characters
    
    Args:
        name (str): Raw material name
        
    Returns:
        str: Sanitized name
    """
    # Remove invalid characters
    name = re.sub(r'[<>:"/\\|?*]', '', name)
    # Limit length
    if len(name) > 60:
        name = name[:60]
    # Ensure not empty
    if not name.strip():
        name = "AI_Material"
    return name.strip()


def get_or_create_material(name):
    """
    Get existing material atau create new one
    
    Args:
        name (str): Material name
        
    Returns:
        Material: Blender material object
    """
    name = sanitize_material_name(name)
    
    # Check if exists
    if name in bpy.data.materials:
        material = bpy.data.materials[name]
    else:
        material = bpy.data.materials.new(name=name)
    
    # Enable nodes
    material.use_nodes = True
    
    return material


def show_message(message, title="Info", icon='INFO'):
    """
    Show message popup di UI
    
    Args:
        message (str): Message to show
        title (str): Popup title
        icon (str): Icon type (INFO, WARNING, ERROR)
    """
    def draw(self, context):
        self.layout.label(text=message)
    
    bpy.context.window_manager.popup_menu(draw, title=title, icon=icon)


def format_prompt_for_display(prompt, max_length=50):
    """
    Format prompt untuk display di UI dengan truncation
    
    Args:
        prompt (str): Original prompt
        max_length (int): Maximum display length
        
    Returns:
        str: Formatted prompt
    """
    if len(prompt) <= max_length:
        return prompt
    return prompt[:max_length-3] + "..."
