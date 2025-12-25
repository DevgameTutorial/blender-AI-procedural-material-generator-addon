"""
Blender AI Procedural Material Generator  
Material Generator - Core engine untuk create shader nodes dari AI config
"""

import bpy
from . import utils


# Node type aliases - mapping nama node yang salah ke yang benar
# AI sering menghasilkan nama yang berbeda dengan class name sebenarnya di Blender
NODE_TYPE_ALIASES = {
    # ColorRamp adalah nama umum, tapi di Blender class name-nya ValToRGB
    "ShaderNodeColorRamp": "ShaderNodeValToRGB",
    "ColorRamp": "ShaderNodeValToRGB",
    
    # Texture nodes - kadang AI lupa prefix "Tex"
    "ShaderNodeNoise": "ShaderNodeTexNoise",
    "ShaderNodeVoronoi": "ShaderNodeTexVoronoi",
    "ShaderNodeBrick": "ShaderNodeTexBrick",
    "ShaderNodeWave": "ShaderNodeTexWave",
    "ShaderNodeMusgrave": "ShaderNodeTexMusgrave",
    "ShaderNodeGradient": "ShaderNodeTexGradient",
    "ShaderNodeMagic": "ShaderNodeTexMagic",
    "ShaderNodeChecker": "ShaderNodeTexChecker",
    
    # Kadang AI menggunakan nama singkat
    "Principled": "ShaderNodeBsdfPrincipled",
    "Emission": "ShaderNodeEmission",
    "Mix": "ShaderNodeMix",
    "MixRGB": "ShaderNodeMixRGB",
    "Bump": "ShaderNodeBump",
    "Mapping": "ShaderNodeMapping",
    "TexCoord": "ShaderNodeTexCoord",
    "Output": "ShaderNodeOutputMaterial",
    
    # Volume nodes - support singkat names
    "VolumeAbsorption": "ShaderNodeVolumeAbsorption",
    "VolumeScatter": "ShaderNodeVolumeScatter",
    "PrincipledVolume": "ShaderNodeVolumePrincipled",
    "VolumePrincipled": "ShaderNodeVolumePrincipled",
    
    # CRITICAL: AI sering salah generate nama ini!
    "ShaderNodeBsdfPrincipledVolume": "ShaderNodeVolumePrincipled",  # ❌ Nama salah → ✅ Nama benar
    "BsdfPrincipledVolume": "ShaderNodeVolumePrincipled",
    
    # Glass and Refraction BSDF - AI sering salah urutan nama (GlassBSDF vs BsdfGlass)
    "ShaderNodeGlassBSDF": "ShaderNodeBsdfGlass",  # ❌ Nama salah → ✅ Nama benar
    "GlassBSDF": "ShaderNodeBsdfGlass",
    "Glass": "ShaderNodeBsdfGlass",
    "ShaderNodeRefractionBSDF": "ShaderNodeBsdfRefraction",  # ❌ Nama salah → ✅ Nama benar
    "RefractionBSDF": "ShaderNodeBsdfRefraction",
    "Refraction": "ShaderNodeBsdfRefraction",
}




def create_material_from_config(config, assign_to_active=True):
    """
    Create material dari AI configuration
    
    Args:
        config (dict): Material configuration dari AI
        assign_to_active (bool): Assign ke active object jika True
        
    Returns:
        Material: Created material atau None jika gagal
    """
    try:
        material_name = config.get('material_name', 'AI_Material')
        
        material = utils.get_or_create_material(material_name)
        
        # =====================================================================
        # PHASE 1: PRE-CREATION VALIDATION & SUMMARY
        # =====================================================================
        print("=" * 70)
        print(f"[Material Generator] 🎬 STARTING MATERIAL CREATION")
        print(f"[Material Generator] Material Name: {material_name}")
        print("=" * 70)
        
        # Validate and summarize configuration
        nodes_config = config.get('nodes', [])
        links_config = config.get('links', [])
        
        print(f"\n📋 CONFIGURATION SUMMARY:")
        print(f"  Total nodes to create: {len(nodes_config)}")
        print(f"  Total links to create: {len(links_config)}")
        
        # Analyze node types
        node_types = {}
        for node in nodes_config:
            node_type = node.get('type', 'Unknown')
            node_types[node_type] = node_types.get(node_type, 0) + 1
        
        print(f"\n📊 NODE BREAKDOWN BY TYPE:")
        for node_type, count in sorted(node_types.items(), key=lambda x: -x[1]):
            print(f"  {node_type}: {count}")
        
        # Validate connectivity requirements
        print(f"\n✓ CONNECTIVITY CHECK:")
        min_required_links = len(nodes_config) - 1
        if len(links_config) >= min_required_links:
            print(f"  ✓ Link count OK: {len(links_config)} links >= {min_required_links} required")
        else:
            print(f"  ⚠ WARNING: Only {len(links_config)} links for {len(nodes_config)} nodes")
            print(f"     (Minimum required: {min_required_links})")
        
        # Check for potential dead nodes
        nodes_in_links = set()
        for link in links_config:
            nodes_in_links.add(link.get('from_node'))
            nodes_in_links.add(link.get('to_node'))
        
        dead_nodes = []
        for i in range(len(nodes_config)):
            if i not in nodes_in_links:
                dead_nodes.append(i)
        
        if dead_nodes:
            print(f"  ⚠ WARNING: {len(dead_nodes)} node(s) not referenced in links:")
            for idx in dead_nodes:
                node_type = nodes_config[idx].get('type', 'Unknown')
                print(f"     Node[{idx}]: {node_type}")
        else:
            print(f"  ✓ All nodes referenced in links")
        
        print("\n" + "=" * 70)
        print("[Material Generator] 🔨 PHASE 2: NODE CREATION")
        print("=" * 70 + "\n")
        
        # Clear existing nodes
        material.node_tree.nodes.clear()
        
        # Create nodes
        node_objects = []
        for i, node_config in enumerate(config['nodes']):
            node = create_node(material, node_config)
            if node:
                node_objects.append(node)
            else:
                print(f"[Material Generator] Failed to create node {i}: {node_config.get('type')}")
        
        # Create links
        success_links = link_nodes(material, links_config, node_objects)
        
        # =====================================================================
        # PHASE 4: POST-CREATION VERIFICATION
        # =====================================================================
        print("\n" + "=" * 70)
        print("[Material Generator] 🔍 PHASE 4: POST-CREATION VERIFICATION")
        print("=" * 70)
        
        # Verify all nodes were created
        print(f"\n📦 NODE CREATION VERIFICATION:")
        print(f"  Requested: {len(nodes_config)} nodes")
        print(f"  Created: {len(node_objects)} nodes")
        
        if len(node_objects) < len(nodes_config):
            failed_count = len(nodes_config) - len(node_objects)
            print(f"  ⚠ WARNING: {failed_count} node(s) failed to create")
        else:
            print(f"  ✓ All nodes created successfully")
        
        # Verify connections
        actual_links = len(material.node_tree.links)
        print(f"\n🔗 CONNECTION VERIFICATION:")
        print(f"  Requested: {len(links_config)} connections")
        print(f"  Successful: {success_links} connections")
        print(f"  Actually in material: {actual_links} links")
        
        # Check for unconnected nodes
        print(f"\n🔌 CONNECTIVITY CHECK:")
        unconnected_nodes = []
        for node in material.node_tree.nodes:
            has_input = any(link.to_node == node for link in material.node_tree.links)
            has_output = any(link.from_node == node for link in material.node_tree.links)
            
            # Skip special cases
            is_coord = node.bl_idname == 'ShaderNodeTexCoord'
            is_output = node.bl_idname == 'ShaderNodeOutputMaterial'
            
            if not has_input and not is_coord:
                unconnected_nodes.append((node.name, "NO INPUT"))
            elif not has_output and not is_output:
                unconnected_nodes.append((node.name, "NO OUTPUT"))
        
        if unconnected_nodes:
            print(f"  ⚠ Found {len(unconnected_nodes)} unconnected node(s):")
            for node_name, issue in unconnected_nodes:
                print(f"     - {node_name}: {issue}")
        else:
            print(f"  ✓ All nodes properly connected")
        
        # Verify path to output
        print(f"\n🎯 OUTPUT REACHABILITY:")
        output_node = None
        for node in material.node_tree.nodes:
            if node.bl_idname == 'ShaderNodeOutputMaterial':
                output_node = node
                break
        
        if output_node:
            # Check if Surface socket is connected
            surface_socket = None
            for inp in output_node.inputs:
                if inp.name == 'Surface':
                    surface_socket = inp
                    break
            
            if surface_socket and surface_socket.is_linked:
                connected_node = surface_socket.links[0].from_node
                print(f"  ✓ Material Output.Surface connected to: {connected_node.name}")
            else:
                print(f"  ⚠ WARNING: Material Output.Surface NOT CONNECTED")
        else:
            print(f"  ❌ ERROR: No Material Output node found!")
        
        print("=" * 70)
        
        # Auto-arrange nodes untuk readability berdasarkan graph connectivity
        arrange_nodes(material, links_config, node_objects)
        
        # =====================================================================
        # FINAL SUMMARY
        # =====================================================================
        print("\n" + "=" * 70)
        print(f"[Material Generator] ✅ MATERIAL CREATION COMPLETE")
        print("=" * 70)
        print(f"  Material: {material.name}")
        print(f"  Nodes: {len(node_objects)} / {len(nodes_config)} requested")
        print(f"  Links: {success_links} / {len(links_config)} requested")
        
        # Determine overall status
        nodes_ok = len(node_objects) == len(nodes_config)
        links_ok = success_links >= len(links_config) * 0.9  # 90% threshold
        overall_status = "SUCCESS" if (nodes_ok and links_ok) else "PARTIAL SUCCESS"
        print(f"  Status: {overall_status}")
        
        # Assign to active object
        if assign_to_active and bpy.context.active_object:
            obj = bpy.context.active_object
            if not obj.data.materials:
                obj.data.materials.append(material)
            else:
                obj.active_material = material
            print(f"  Assigned to: {obj.name}")
        
        print("=" * 70 + "\n")
        
        return material
        
    except Exception as e:
        print(f"[Material Generator] Error creating material: {str(e)}")
        import traceback
        traceback.print_exc()
        return None


def create_node(material, node_config):
    """
    Create individual shader node
    
    Args:
        material: Blender material
        node_config (dict): Node configuration
        
    Returns:
        Node: Created node atau None
    """
    try:
        node_type = node_config['type']
        nodes = material.node_tree.nodes
        
        # Convert node type using aliases if needed
        if node_type in NODE_TYPE_ALIASES:
            original_type = node_type
            node_type = NODE_TYPE_ALIASES[node_type]
            print(f"[Material Generator] ⚠ Converted node type: {original_type} → {node_type}")
        
        # Create node
        node = nodes.new(type=node_type)
        
        # Set location
        if 'location' in node_config:
            node.location = node_config['location']
        
        # Set name jika ada
        if 'name' in node_config:
            node.name = node_config['name']
        
        # CRITICAL FIX: Set node-specific properties BEFORE setting inputs!
        # WHY: For Mix node, data_type property must be set FIRST so that
        # sockets 'A' and 'B' are in correct state (RGBA/VECTOR/FLOAT) before
        # receiving values. If inputs are set before properties, sockets may
        # be in wrong type and reject valid data (e.g., RGBA array rejected by FLOAT socket).
        set_node_properties(node, node_config)
        
        # Set inputs AFTER properties are configured
        if 'inputs' in node_config:
            for input_name, value in node_config['inputs'].items():
                # SPECIAL HANDLING for Mix nodes: use index-based socket finding
                if node.bl_idname == 'ShaderNodeMix':
                    input_socket = find_socket_for_mix_node(node, input_name, "input")
                    if not input_socket:
                        # Fallback to name-based search
                        if input_name in node.inputs:
                            input_socket = node.inputs[input_name]
                        else:
                            print(f"[Material Generator] ⚠ Mix node: Socket '{input_name}' not found")
                            continue
                else:
                    # Normal nodes: use name-based search
                    if input_name in node.inputs:
                        input_socket = node.inputs[input_name]
                    else:
                        continue
                
                # CRITICAL FIX: Extract actual value if AI returns nested dict
                # This must happen for ALL nodes, not just non-Mix nodes
                # Sometimes AI returns {"Scale": {"default_value": 5.0}} instead of {"Scale": 5.0}
                if isinstance(value, dict):
                    # Try to extract default_value or first value
                    if 'default_value' in value:
                        value = value['default_value']
                    elif value:
                        # Get first value from dict
                        value = list(value.values())[0]
                    else:
                        print(f"[Material Generator] Warning: Empty dict for {input_name}, skipping")
                        continue
                
                # Set value based on type - THIS MUST HAPPEN FOR ALL NODES
                if hasattr(input_socket, 'default_value'):
                    try:
                        # CRITICAL: Detect socket type to handle 3D vs 4D dimensions
                        socket_name_lower = input_name.lower()
                        is_vector_socket = any(keyword in socket_name_lower for keyword in 
                            ['vector', 'normal', 'displacement', 'tangent', 'clearcoat'])
                        is_color_socket = 'color' in socket_name_lower or input_name.lower() in ['a', 'b']  # Mix node A/B sockets
                        
                        # Special case: Mapping Scale/Location/Rotation need Vector [X,Y,Z], not float
                        is_mapping_vector_param = (node.bl_idname == 'ShaderNodeMapping' and 
                                                  input_name in ['Scale', 'Location', 'Rotation'])
                        
                        # Detect float-only sockets (Fac, Height, Detail, etc)
                        # EXCLUDE Mapping.Scale/Location/Rotation as they need vectors
                        is_float_socket = (any(keyword in socket_name_lower for keyword in 
                            ['fac', 'factor', 'height', 'detail', 'roughness', 'strength', 
                             'distance', 'distortion', 'metallic', 'specular', 'w', 'phase']) 
                            and not is_mapping_vector_param)
                        
                        # Special handling: Convert float to vector for Mapping parameters
                        if is_mapping_vector_param:
                            if isinstance(value, (int, float)):
                                # Convert single value to uniform vector [v, v, v]
                                print(f"[Material Generator] Converting {value} to uniform vector for '{input_name}'")
                                input_socket.default_value = [float(value), float(value), float(value)]
                                continue
                            elif isinstance(value, (list, tuple)) and len(value) == 3:
                                # Already a 3D vector
                                input_socket.default_value = value
                                continue
                            # If list but not 3 elements, fall through to normal handling
                        
                        # =========================================================
                        # EARLY VALIDATION: Detect obviously wrong values
                        # =========================================================
                        
                        # CHECK 1: String marker values (AI sends "must_connect" etc)
                        if isinstance(value, str):
                            if value.lower() in ['must_connect', 'connect', 'link', 'from_node']:
                                print(f"[Material Generator] ℹ️  '{input_name}' marked as '{value}' - will be set via links, skipping direct value")
                                continue  # Skip, will be connected via links
                        
                        # CHECK 2: Array too long (AI sent node indices array!)
                        if isinstance(value, (list, tuple)) and len(value) > 10:
                            value_len = len(value)
                            print(f"[Material Generator] ⚠️  INVALID INPUT: '{input_name}' has {value_len} elements (likely AI sent node indices!)")
                            
                            # Intelligent fallback based on socket type
                            if is_color_socket:
                                print(f"[Material Generator]   → Using default color [0.8, 0.8, 0.8, 1.0] (light gray)")
                                input_socket.default_value = [0.8, 0.8, 0.8, 1.0]
                            elif is_vector_socket:
                                print(f"[Material Generator]   → Using default vector [0.0, 0.0, 0.0]")
                                input_socket.default_value = [0.0, 0.0, 0.0]
                            elif is_float_socket:
                                print(f"[Material Generator]   → Using first element as float: {value[0]}")
                                input_socket.default_value = float(value[0]) if len(value) > 0 else 0.0
                            else:
                                print(f"[Material Generator]   → Skipping this input (will use Blender default or link)")
                            continue
                        
                        # EARLY DETECTION: List sent to float socket (common AI error!)
                        if isinstance(value, (list, tuple)) and is_float_socket:
                            if len(value) > 0:
                                # Convert list to float by taking first element
                                print(f"[Material Generator] ⚠ Converting list {value} to float for socket '{input_name}' (using first value)")
                                input_socket.default_value = float(value[0])
                            else:
                                print(f"[Material Generator] ⚠ Empty list for socket '{input_name}', using 0.0")
                                input_socket.default_value = 0.0
                            continue  # Skip to next input
                        
                        # Smart dimension handling for arrays
                        if isinstance(value, (list, tuple)):
                            value_len = len(value)
                            
                            # Handle 4-element arrays
                            if value_len == 4:
                                if is_vector_socket:
                                    # Vector/Normal sockets need 3D (XYZ), convert from 4D (XYZW or RGBA)
                                    print(f"[Material Generator] Converting 4D→3D for Vector socket '{input_name}'")
                                    input_socket.default_value = list(value[:3])
                                else:
                                    # Color sockets accept 4D (RGBA)
                                    input_socket.default_value = value
                            
                            # Handle 3-element arrays
                            elif value_len == 3:
                                if is_color_socket:
                                    # Color sockets need 4D (RGBA), add alpha=1.0
                                    print(f"[Material Generator] Converting 3D→4D for Color socket '{input_name}' (adding alpha)")
                                    input_socket.default_value = list(value) + [1.0]
                                else:
                                    # Vector sockets accept 3D (XYZ)
                                    input_socket.default_value = value
                            
                            # Handle 5+ element arrays (legacy handling)
                            elif value_len == 5:
                                # AI sent 5 values, take first 4 (RGBA) or first 3 (XYZ)
                                if is_vector_socket:
                                    print(f"[Material Generator] Warning: {input_name} has 5 values, using first 3 (XYZ)")
                                    input_socket.default_value = list(value[:3])
                                else:
                                    print(f"[Material Generator] Warning: {input_name} has 5 values, using first 4 (RGBA)")
                                    input_socket.default_value = list(value[:4])
                            
                            elif value_len > 5:
                                # Too many values
                                if is_vector_socket:
                                    print(f"[Material Generator] Warning: {input_name} has {value_len} values, using first 3")
                                    input_socket.default_value = list(value[:3])
                                else:
                                    print(f"[Material Generator] Warning: {input_name} has {value_len} values, using first 4")
                                    input_socket.default_value = list(value[:4])
                            else:
                                # Unusual length (1 or 2 elements)
                                print(f"[Material Generator] Warning: {input_name} has unusual length {value_len}")
                                input_socket.default_value = value
                        else:
                            # Single value (float/int)
                            input_socket.default_value = value
                            
                    except TypeError as e:
                        # Fallback: handle remaining conversion issues
                        try:
                            # Check if value is still a list/tuple (fallback dari deteksi awal)
                            if isinstance(value, (list, tuple)):
                                if len(value) > 0:
                                    # Ambil elemen pertama sebagai fallback
                                    print(f"[Material Generator] ⚠ TypeError fallback: Converting list {value} to float for '{input_name}' (using first element)")
                                    input_socket.default_value = float(value[0])
                                else:
                                    print(f"[Material Generator] ⚠ TypeError fallback: Empty list for '{input_name}', using 0.0")
                                    input_socket.default_value = 0.0
                            elif isinstance(value, str):
                                try:
                                    input_socket.default_value = float(value)
                                except ValueError:
                                    print(f"[Material Generator] Cannot convert {input_name} string value '{value}' to float, skipping")
                                    continue
                            else:
                                # Try direct conversion
                                input_socket.default_value = float(value)
                        except (ValueError, TypeError) as e:
                            print(f"[Material Generator] Cannot convert {input_name} value {value}: {e}")
                            continue  # Skip this input instead of crashing
                    except Exception as e:
                        print(f"[Material Generator] Failed to set input {input_name}: {str(e)}")
        
        # =====================================================================
        # NEW: Check if important inputs are set (read from node_reference)
        # =====================================================================
        import node_reference
        
        node_metadata = node_reference.NODE_TYPES.get(node.bl_idname, {})
        critical_inputs = node_metadata.get('critical_inputs', {})
        
        if critical_inputs:
            for socket_name in critical_inputs.keys():
                if socket_name not in node_config.get('inputs', {}):
                    reason = critical_inputs[socket_name].get('reason', 'akan gunakan default Blender')
                    print(f"[Material Generator] ℹ️  Node {node.name} ({node.bl_idname}): "
                          f"'{socket_name}' not set - {reason}")
        
        # =====================================================================
        # Enhanced: Log successful node creation with socket info
        # =====================================================================
        print(f"[Material Generator] ✓ NODE CREATED: {node.name} ({node.bl_idname})")
        
        # Show inputs summary
        if len(node.inputs) > 0:
            print(f"  📥 Inputs ({len(node.inputs)} total):")
            for idx, inp in enumerate(node.inputs):
                sock_type = inp.type if hasattr(inp, 'type') else "?"
                default_val = ""
                if hasattr(inp, 'default_value'):
                    try:
                        # Try to get default value for display
                        val = inp.default_value
                        if isinstance(val, (list, tuple)):
                            default_val = f" = {[round(v, 3) if isinstance(v, float) else v for v in val]}"
                        elif isinstance(val, float):
                            default_val = f" = {round(val, 3)}"
                        else:
                            default_val = f" = {val}"
                    except:
                        pass  # Some sockets can't access default_value
                print(f"     [{idx}] {inp.name} (type: {sock_type}){default_val}")
        
        # Show outputs summary
        if len(node.outputs) > 0:
            print(f"  📤 Outputs ({len(node.outputs)} total):")
            for idx, out in enumerate(node.outputs):
                sock_type = out.type if hasattr(out, 'type') else "?"
                print(f"     [{idx}] {out.name} (type: {sock_type})")
        
        # Show important properties for specific node types
        if node.bl_idname == 'ShaderNodeMix' and hasattr(node, 'data_type'):
            print(f"  ⚙️  data_type: {node.data_type}")
            if hasattr(node, 'blend_type'):
                print(f"  ⚙️  blend_type: {node.blend_type}")
        elif node.bl_idname == 'ShaderNodeTexVoronoi' and hasattr(node, 'feature'):
            print(f"  ⚙️  feature: {node.feature}")
            if hasattr(node, 'distance'):
                print(f"  ⚙️  distance: {node.distance}")
        elif node.bl_idname == 'ShaderNodeMath' and hasattr(node, 'operation'):
            print(f"  ⚙️  operation: {node.operation}")
        elif node.bl_idname == 'ShaderNodeVectorMath' and hasattr(node, 'operation'):
            print(f"  ⚙️  operation: {node.operation}")
        
        return node
        
    except Exception as e:
        print(f"[Material Generator] Error creating node {node_config.get('type')}: {str(e)}")
        return None


def set_node_properties(node, node_config):
    """
    Set node-specific properties (selain inputs)
    
    Args:
        node: Blender node
        node_config (dict): Node configuration
    """
    try:
        # ColorRamp - setup color stops
        if node.bl_idname == 'ShaderNodeValToRGB':
            if 'color_ramp' in node_config:
                ramp_data = node_config['color_ramp']
                
                # Safe handling: check if ramp_data is None or not a dict
                if ramp_data is None or not isinstance(ramp_data, dict):
                    print(f"[Material Generator] ⚠️  ColorRamp missing configuration - generating smart default")
                    # AUTO-GENERATE smart default (warm brown gradient - universal fallback)
                    ramp_data = {
                        'stops': [
                            {'position': 0.0, 'color': [0.2, 0.15, 0.1, 1.0]},   # Dark brown
                            {'position': 0.5, 'color': [0.5, 0.4, 0.3, 1.0]},    # Medium brown
                            {'position': 1.0, 'color': [0.8, 0.7, 0.6, 1.0]}     # Light brown
                        ]
                    }
                    print(f"[Material Generator] ✓ Using smart gradient (warm brown) instead of black-white")
                
                color_ramp = node.color_ramp
                
                # Get stops data
                stops = ramp_data.get('stops', [])
                if stops and isinstance(stops, list):
                    # Clear existing elements (keep minimum 2)
                    while len(color_ramp.elements) > 2:
                        color_ramp.elements.remove(color_ramp.elements[0])
                    
                    # Create/update elements
                    for i, stop in enumerate(stops):
                        if not isinstance(stop, dict):
                            print(f"[Material Generator] Warning: color_ramp stop {i} is not a dict, skipping")
                            continue
                        
                        if i >= len(color_ramp.elements):
                            color_ramp.elements.new(stop.get('position', 0.5))
                        
                        element = color_ramp.elements[i]
                        element.position = stop.get('position', 0.5)
                        
                        # Validate color value (must be 4 elements: RGBA)
                        color_value = stop.get('color', [1.0, 1.0, 1.0, 1.0])
                        if isinstance(color_value, (list, tuple)):
                            if len(color_value) == 4:
                                element.color = color_value
                            elif len(color_value) == 3:
                                element.color = list(color_value) + [1.0]
                            elif len(color_value) > 4:
                                # Take first 4 values
                                element.color = list(color_value[:4])
                            else:
                                print(f"[Material Generator] Warning: Invalid color length {len(color_value)} for stop {i}")
                                element.color = [1.0, 1.0, 1.0, 1.0]
                        else:
                            element.color = [1.0, 1.0, 1.0, 1.0]
                    
                    print(f"[Material Generator] ColorRamp setup with {len(stops)} stops")
            
            # Set color_mode if specified
            if 'color_mode' in node_config and node_config['color_mode'] is not None:
                color_mode_value = str(node_config['color_mode']).upper()
                valid_color_modes = ['RGB', 'HSV', 'HSL']
                if color_mode_value in valid_color_modes:
                    color_ramp.color_mode = color_mode_value
                    print(f"[Material Generator] ColorRamp color_mode: {color_mode_value}")
                else:
                    print(f"[Material Generator] ⚠ Invalid color_mode '{node_config['color_mode']}', using 'RGB' as fallback")
                    color_ramp.color_mode = 'RGB'
            
            # Set interpolation if specified
            if 'interpolation' in node_config and node_config['interpolation'] is not None:
                interp_value = str(node_config['interpolation']).upper()
                # Blender uses different enum name: B_SPLINE not BSPLINE
                if interp_value == 'BSPLINE':
                    interp_value = 'B_SPLINE'
                valid_interpolations = ['CONSTANT', 'LINEAR', 'EASE', 'CARDINAL', 'B_SPLINE']
                if interp_value in valid_interpolations:
                    color_ramp.interpolation = interp_value
                    print(f"[Material Generator] ColorRamp interpolation: {interp_value}")
                else:
                    print(f"[Material Generator] ⚠ Invalid interpolation '{node_config['interpolation']}', using 'LINEAR' as fallback")
                    color_ramp.interpolation = 'LINEAR'
                    
        
        # Noise Texture properties
        if node.bl_idname == 'ShaderNodeTexNoise':
            if 'noise_dimensions' in node_config and node_config['noise_dimensions'] is not None:
                noise_dims_value = str(node_config['noise_dimensions']).upper()
                valid_noise_dims = ['1D', '2D', '3D', '4D']
                if noise_dims_value in valid_noise_dims:
                    node.noise_dimensions = noise_dims_value
                    print(f"[Material Generator] Noise dimensions: {noise_dims_value}")
                else:
                    print(f"[Material Generator] ⚠ Invalid noise_dimensions '{node_config['noise_dimensions']}', using '3D' as fallback")
                    node.noise_dimensions = '3D'
        
        # Mix node (new Blender 3.4+) - CRITICAL property setup
        if node.bl_idname == 'ShaderNodeMix':
            # Set data_type first - this determines socket behavior
            if 'data_type' in node_config and node_config['data_type'] is not None:
                data_type_value = str(node_config['data_type']).upper()
                valid_data_types = ['FLOAT', 'VECTOR', 'RGBA']
                if data_type_value in valid_data_types:
                    node.data_type = data_type_value
                    print(f"[Material Generator] Mix data_type: {data_type_value}")
                    
                    # HIDE irrelevant sockets to reduce confusion!
                    # Mix node shows ALL sockets but only some are relevant per data_type
                    hide_unused_mix_sockets(node, data_type_value)
                else:
                    print(f"[Material Generator] ⚠ Invalid Mix data_type: {data_type_value}, using FLOAT")
                    node.data_type = 'FLOAT'
                    hide_unused_mix_sockets(node, 'FLOAT')
            
            # Set blend_type (only relevant for RGBA)
            if 'blend_type' in node_config and node_config['blend_type'] is not None:
                blend_type_value = str(node_config['blend_type']).upper()
                valid_blend_types = [
                    'MIX', 'DARKEN', 'MULTIPLY', 'BURN', 'LIGHTEN', 'SCREEN', 
                    'DODGE', 'ADD', 'OVERLAY', 'SOFT_LIGHT', 'LINEAR_LIGHT', 
                    'DIFFERENCE', 'EXCLUSION', 'SUBTRACT', 'DIVIDE', 
                    'HUE', 'SATURATION', 'COLOR', 'VALUE'
                ]
                if blend_type_value in valid_blend_types:
                    node.blend_type = blend_type_value
                    print(f"[Material Generator] Mix blend_type (color): {blend_type_value}")
                else:
                    print(f"[Material Generator] ⚠ Invalid blend_type '{node_config['blend_type']}', using 'MIX' as fallback")
                    node.blend_type = 'MIX'
        
        # Wave Texture properties
        if node.bl_idname == 'ShaderNodeTexWave':
            if 'wave_type' in node_config and node_config['wave_type'] is not None:
                # Convert to uppercase (Blender enum)
                wave_type_value = str(node_config['wave_type']).upper()
                valid_wave_types = ['BANDS', 'RINGS']
                if wave_type_value in valid_wave_types:
                    node.wave_type = wave_type_value
                    print(f"[Material Generator] Wave type: {wave_type_value}")
                else:
                    print(f"[Material Generator] ⚠ Invalid wave_type '{node_config['wave_type']}', using 'BANDS' as fallback")
                    node.wave_type = 'BANDS'
            
            if 'bands_direction' in node_config and node_config['bands_direction'] is not None:
                bands_dir = str(node_config['bands_direction']).upper()
                node.bands_direction = bands_dir if bands_dir in ['X', 'Y', 'Z', 'DIAGONAL'] else 'X'
            
            if 'rings_direction' in node_config and node_config['rings_direction'] is not None:
                rings_dir = str(node_config['rings_direction']).upper()
                node.rings_direction = rings_dir if rings_dir in ['X', 'Y', 'Z', 'SPHERICAL'] else 'X'
            
            if 'wave_profile' in node_config and node_config['wave_profile'] is not None:
                wave_prof = str(node_config['wave_profile']).upper()
                node.wave_profile = wave_prof if wave_prof in ['SIN', 'SAW', 'TRI'] else 'SIN'
        
        # Voronoi Texture properties
        if node.bl_idname == 'ShaderNodeTexVoronoi':
            if 'feature' in node_config and node_config['feature'] is not None:
                # Convert to uppercase (Blender enum)
                feature_value = str(node_config['feature']).upper()
                valid_features = ['F1', 'F2', 'SMOOTH_F1', 'DISTANCE_TO_EDGE', 'N_SPHERE_RADIUS']
                if feature_value in valid_features:
                    node.feature = feature_value
                    print(f"[Material Generator] Voronoi feature: {feature_value}")
                else:
                    print(f"[Material Generator] ⚠ Invalid voronoi feature '{node_config['feature']}', using 'F1' as fallback")
                    node.feature = 'F1'
            
            if 'distance' in node_config and node_config['distance'] is not None:
                distance_value = str(node_config['distance']).upper()
                valid_distances = ['EUCLIDEAN', 'MANHATTAN', 'CHEBYCHEV', 'MINKOWSKI']
                node.distance = distance_value if distance_value in valid_distances else 'EUCLIDEAN'
            
            if 'voronoi_dimensions' in node_config and node_config['voronoi_dimensions'] is not None:
                node.voronoi_dimensions = str(node_config['voronoi_dimensions'])
        
        # Musgrave Texture properties
        if node.bl_idname == 'ShaderNodeTexMusgrave':
            if 'musgrave_type' in node_config and node_config['musgrave_type'] is not None:
                # Convert to uppercase (Blender enum)
                musgrave_value = str(node_config['musgrave_type']).upper()
                valid_musgrave = ['MULTIFRACTAL', 'RIDGED_MULTIFRACTAL', 'HYBRID_MULTIFRACTAL', 'FBM', 'HETERO_TERRAIN']
                if musgrave_value in valid_musgrave:
                    node.musgrave_type = musgrave_value
                    print(f"[Material Generator] Musgrave type: {musgrave_value}")
                else:
                    print(f"[Material Generator] ⚠ Invalid musgrave_type '{node_config['musgrave_type']}', using 'FBM' as fallback")
                    node.musgrave_type = 'FBM'
            
            if 'musgrave_dimensions' in node_config and node_config['musgrave_dimensions'] is not None:
                node.musgrave_dimensions = str(node_config['musgrave_dimensions'])
        
        # Gradient Texture properties
        if node.bl_idname == 'ShaderNodeTexGradient':
            if 'gradient_type' in node_config and node_config['gradient_type'] is not None:
                # Convert to uppercase (Blender enum)
                gradient_value = str(node_config['gradient_type']).upper()
                valid_gradients = ['LINEAR', 'QUADRATIC', 'EASING', 'DIAGONAL', 'SPHERICAL', 'QUADRATIC_SPHERE', 'RADIAL']
                node.gradient_type = gradient_value if gradient_value in valid_gradients else 'LINEAR'
        
        # Mix RGB node - set blend mode
        if node.bl_idname == 'ShaderNodeMixRGB':
            if 'blend_type' in node_config and node_config['blend_type'] is not None:
                # Convert to uppercase (Blender requires uppercase enum values)
                # AI might send "Mix" but Blender needs "MIX"
                blend_type_value = str(node_config['blend_type']).upper()
                
                # Valid blend types in Blender
                valid_blend_types = [
                    'MIX', 'DARKEN', 'MULTIPLY', 'BURN', 'LIGHTEN', 'SCREEN', 
                    'DODGE', 'ADD', 'OVERLAY', 'SOFT_LIGHT', 'LINEAR_LIGHT', 
                    'DIFFERENCE', 'EXCLUSION', 'SUBTRACT', 'DIVIDE', 
                    'HUE', 'SATURATION', 'COLOR', 'VALUE'
                ]
                
                if blend_type_value in valid_blend_types:
                    node.blend_type = blend_type_value
                    print(f"[Material Generator] Mix blend_type: {blend_type_value}")
                else:
                    # Fallback to MIX if invalid
                    print(f"[Material Generator] ⚠ Invalid blend_type '{node_config['blend_type']}', using 'MIX' as fallback")
                    node.blend_type = 'MIX'
        
        # Math node - set operation
        if node.bl_idname == 'ShaderNodeMath':
            if 'operation' in node_config and node_config['operation'] is not None:
                # Convert to uppercase (Blender enum)
                math_op = str(node_config['operation']).upper()
                valid_math_ops = [
                    'ADD', 'SUBTRACT', 'MULTIPLY', 'DIVIDE', 'MULTIPLY_ADD',
                    'POWER', 'LOGARITHM', 'SQRT', 'INVERSE_SQRT', 'ABSOLUTE',
                    'EXPONENT', 'MINIMUM', 'MAXIMUM', 'LESS_THAN', 'GREATER_THAN',
                    'SIGN', 'COMPARE', 'SMOOTH_MIN', 'SMOOTH_MAX', 'ROUND',
                    'FLOOR', 'CEIL', 'TRUNC', 'FRACT', 'MODULO', 'WRAP',
                    'SNAP', 'PINGPONG', 'SINE', 'COSINE', 'TANGENT',
                    'ARCSINE', 'ARCCOSINE', 'ARCTANGENT', 'ARCTAN2',
                    'SINH', 'COSH', 'TANH', 'RADIANS', 'DEGREES'
                ]
                if math_op in valid_math_ops:
                    node.operation = math_op
                    print(f"[Material Generator] Math operation: {math_op}")
                else:
                    print(f"[Material Generator] ⚠ Invalid math operation '{node_config['operation']}', using 'ADD' as fallback")
                    node.operation = 'ADD'
            
            if 'use_clamp' in node_config and node_config['use_clamp'] is not None:
                node.use_clamp = node_config['use_clamp']
        
        # Vector Math node - set operation
        if node.bl_idname == 'ShaderNodeVectorMath':
            if 'operation' in node_config and node_config['operation'] is not None:
                # Convert to uppercase (Blender enum)
                vec_math_op = str(node_config['operation']).upper()
                valid_vec_math_ops = [
                    'ADD', 'SUBTRACT', 'MULTIPLY', 'DIVIDE', 'MULTIPLY_ADD',
                    'CROSS_PRODUCT', 'PROJECT', 'REFLECT', 'REFRACT',
                    'FACEFORWARD', 'DOT_PRODUCT', 'DISTANCE', 'LENGTH',
                    'SCALE', 'NORMALIZE', 'ABSOLUTE', 'MINIMUM', 'MAXIMUM',
                    'FLOOR', 'CEIL', 'FRACTION', 'MODULO', 'WRAP', 'SNAP',
                    'SINE', 'COSINE', 'TANGENT'
                ]
                if vec_math_op in valid_vec_math_ops:
                    node.operation = vec_math_op
                    print(f"[Material Generator] VectorMath operation: {vec_math_op}")
                else:
                    print(f"[Material Generator] ⚠ Invalid vector math operation '{node_config['operation']}', using 'ADD' as fallback")
                    node.operation = 'ADD'
        
        # Mapping node
        if node.bl_idname == 'ShaderNodeMapping':
            if 'vector_type' in node_config and node_config['vector_type'] is not None:
                # Convert to uppercase (Blender enum)
                vec_type = str(node_config['vector_type']).upper()
                valid_vec_types = ['POINT', 'TEXTURE', 'VECTOR', 'NORMAL']
                node.vector_type = vec_type if vec_type in valid_vec_types else 'POINT'
        
        # Mix Shader node
        if node.bl_idname == 'ShaderNodeMixShader':
            # MixShader doesn't have properties, only inputs
            pass
        
        # Hue Saturation node
        if node.bl_idname == 'ShaderNodeHueSaturation':
            # Properties handled via inputs
            pass
        
        # Normal Map node
        if node.bl_idname == 'ShaderNodeNormalMap':
            if 'space' in node_config and node_config['space'] is not None:
                node.space = node_config['space']
            if 'uv_map' in node_config and node_config['uv_map'] is not None:
                node.uv_map = node_config['uv_map']
        
        # Bump node
        if node.bl_idname == 'ShaderNodeBump':
            if 'invert' in node_config and node_config['invert'] is not None:
                node.invert = node_config['invert']
            
    except Exception as e:
        print(f"[Material Generator] Error setting node properties: {str(e)}")
        import traceback
        traceback.print_exc()



def link_nodes(material, links_config, node_objects):
    """
    Create links between nodes
    
    Args:
        material: Blender material
        links_config (list): List of link configurations
        node_objects (list): List of created node objects
        
    Returns:
        int: Number of successful links
    """
    # =====================================================================
    # PHASE 3: LINKING NODES WITH STATISTICS TRACKING
    # =====================================================================
    print("\n" + "=" * 70)
    print("[Material Generator] 🔗 PHASE 3: LINKING NODES")
    print("=" * 70)
    print(f"\nTotal connections to create: {len(links_config)}\n")
    
    # Track connection statistics
    connection_stats = {
        'attempted': 0,
        'successful': 0,
        'failed_socket_not_found': 0,
        'failed_incompatible': 0,
        'failed_other': 0
    }
    
    links = material.node_tree.links
    success_count = 0
    failed_links = []
    
    for i, link_config in enumerate(links_config):
        # Increment attempted di awal loop - hanya 1x per link
        connection_stats['attempted'] += 1
        
        try:
            from_idx = link_config['from_node']
            to_idx = link_config['to_node']
            from_socket_name = link_config['from_socket']
            to_socket_name = link_config['to_socket']
            
            # Validate indices
            if from_idx >= len(node_objects) or to_idx >= len(node_objects):
                failed_links.append(f"Link {i}: Invalid node index {from_idx} or {to_idx}")
                connection_stats['failed_other'] += 1
                continue
            
            from_node = node_objects[from_idx]
            to_node = node_objects[to_idx]
            
            # Find sockets with flexible matching AND handling same-named sockets
            # Pass node object for special handling (e.g., Mix nodes)
            from_socket = find_socket_smart(from_node.outputs, from_socket_name, "output", from_node)
            to_socket = find_socket_smart(to_node.inputs, to_socket_name, "input", to_node)
            
            if from_socket and to_socket:
                # Try to create link
                try:
                    new_link = links.new(from_socket, to_socket)
                    
                    # CRITICAL FIX: Verify link was actually created by checking if it exists
                    # Blender may silently reject incompatible socket connections
                    # We need to check if the new_link object is valid AND exists in the node tree
                    link_created = False
                    
                    # Method 1: Check if new_link is not None and has valid properties
                    if new_link is not None:
                        try:
                            # Try to access link properties - will fail if link was rejected
                            _ = new_link.from_socket
                            _ = new_link.to_socket
                            # If we got here, link exists
                            link_created = True
                        except (AttributeError, ReferenceError):
                            # Link was rejected/deleted by Blender
                            link_created = False
                    
                    # Method 2: Double-check by searching in actual links collection
                    if link_created:
                        # Verify the link actually exists in the material's links
                        # CRITICAL FIX: Use as_pointer() to compare socket identity
                        # Direct comparison (link.from_socket == from_socket) triggers
                        # "bpy_prop_collection.__contains__: expected a string or a tuple of strings" error
                        found_in_links = False
                        from_ptr = from_socket.as_pointer()
                        to_ptr = to_socket.as_pointer()
                        for link in material.node_tree.links:
                            if (link.from_socket.as_pointer() == from_ptr and 
                                link.to_socket.as_pointer() == to_ptr):
                                found_in_links = True
                                break
                        link_created = found_in_links
                    
                    if link_created:
                        success_count += 1
                        connection_stats['successful'] += 1
                        # Enhanced success message with detailed info
                        from_type = f" (type: {from_socket.type})" if hasattr(from_socket, 'type') else ""
                        to_type = f" (type: {to_socket.type})" if hasattr(to_socket, 'type') else ""
                        # CRITICAL FIX: Cannot use 'in' operator with bpy_prop_collection
                        # Use try-except to safely get socket index
                        try:
                            from_idx_info = [s.as_pointer() for s in from_node.outputs].index(from_socket.as_pointer())
                        except (ValueError, AttributeError):
                            from_idx_info = "?"
                        
                        try:
                            to_idx_info = [s.as_pointer() for s in to_node.inputs].index(to_socket.as_pointer())
                        except (ValueError, AttributeError):
                            to_idx_info = "?"
                        
                        print(f"[Material Generator] ✓ LINK SUCCESS")
                        print(f"  From: {from_node.name} ({from_node.bl_idname})")
                        print(f"    └─ Output[{from_idx_info}]: {from_socket.name}{from_type}")
                        print(f"  To:   {to_node.name} ({to_node.bl_idname})")
                        print(f"    └─ Input[{to_idx_info}]: {to_socket.name}{to_type}")
                    else:
                        # Link was rejected by Blender (incompatible socket types)
                        # Enhanced error message with comprehensive debugging info
                        error_msg = f"Link {i}: ❌ CONNECTION FAILED - Blender rejected (incompatible socket types)"
                        error_msg += f"\n  ┌─ FROM NODE: {from_node.name} ({from_node.bl_idname})"
                        
                        # CRITICAL FIX: Safe socket index lookup
                        try:
                            from_idx = [s.as_pointer() for s in from_node.outputs].index(from_socket.as_pointer())
                        except (ValueError, AttributeError):
                            from_idx = "?"
                        from_type = from_socket.type if hasattr(from_socket, 'type') else "unknown"
                        error_msg += f"\n  │  └─ Output[{from_idx}]: '{from_socket.name}' (type: {from_type})"
                        
                        error_msg += f"\n  └─ TO NODE: {to_node.name} ({to_node.bl_idname})"
                        
                        # CRITICAL FIX: Safe socket index lookup
                        try:
                            to_idx = [s.as_pointer() for s in to_node.inputs].index(to_socket.as_pointer())
                        except (ValueError, AttributeError):
                            to_idx = "?"
                        to_type = to_socket.type if hasattr(to_socket, 'type') else "unknown"
                        error_msg += f"\n     └─ Input[{to_idx}]: '{to_socket.name}' (type: {to_type})"
                        
                        # Check for common Mix node issues
                        if from_node.bl_idname == 'ShaderNodeMix' or to_node.bl_idname == 'ShaderNodeMix':
                            mix_node = from_node if from_node.bl_idname == 'ShaderNodeMix' else to_node
                            if hasattr(mix_node, 'data_type'):
                                error_msg += f"\n  ⚠ Mix node data_type: {mix_node.data_type}"
                                error_msg += f"\n     (Ensure socket types match this data_type!)"
                            else:
                                error_msg += f"\n  ⚠ Mix node missing data_type property!"
                        
                        # Add helpful info about available sockets
                        error_msg += f"\n  📋 Available outputs from {from_node.name}:"
                        for idx, out_sock in enumerate(from_node.outputs):
                            sock_type = out_sock.type if hasattr(out_sock, 'type') else "?"
                            error_msg += f"\n     [{idx}] {out_sock.name} (type: {sock_type})"
                        
                        error_msg += f"\n  📋 Available inputs to {to_node.name}:"
                        for idx, in_sock in enumerate(to_node.inputs):
                            sock_type = in_sock.type if hasattr(in_sock, 'type') else "?"
                            linked = " [LINKED]" if hasattr(in_sock, 'is_linked') and in_sock.is_linked else ""
                            hidden = " [HIDDEN]" if hasattr(in_sock, 'hide') and in_sock.hide else ""
                            error_msg += f"\n     [{idx}] {in_sock.name} (type: {sock_type}){linked}{hidden}"
                        
                        connection_stats['failed_incompatible'] += 1
                        failed_links.append(error_msg)
                        
                except Exception as link_error:
                    # Safe error message creation - menggunakan socket_name dari config, bukan from_socket.name
                    # karena accessing socket.name bisa trigger bpy_prop_collection error
                    error_msg = f"Link {i}: Exception during link creation - {str(link_error)}"
                    error_msg += f"\n    {from_node.name}.{from_socket_name} → {to_node.name}.{to_socket_name}"
                    connection_stats['failed_other'] += 1
                    failed_links.append(error_msg)
            else:
                # Enhanced error message when socket not found
                error_msg = f"Link {i}: ❌ SOCKET NOT FOUND"
                error_msg += f"\n  Attempting to connect:"
                error_msg += f"\n    {from_node.name} ({from_node.bl_idname})['{from_socket_name}']"
                error_msg += f"\n    → {to_node.name} ({to_node.bl_idname})['{to_socket_name}']"
                
                if not from_socket:
                    error_msg += f"\n  ⚠ Output socket '{from_socket_name}' NOT FOUND in {from_node.name}"
                    error_msg += f"\n  📋 Available outputs from {from_node.name}:"
                    for idx, out_sock in enumerate(from_node.outputs):
                        sock_type = out_sock.type if hasattr(out_sock, 'type') else "?"
                        error_msg += f"\n     [{idx}] {out_sock.name} (type: {sock_type})"
                
                if not to_socket:
                    error_msg += f"\n  ⚠ Input socket '{to_socket_name}' NOT FOUND in {to_node.name}"
                    error_msg += f"\n  📋 Available inputs to {to_node.name}:"
                    for idx, in_sock in enumerate(to_node.inputs):
                        sock_type = in_sock.type if hasattr(in_sock, 'type') else "?"
                        linked = " [LINKED]" if hasattr(in_sock, 'is_linked') and in_sock.is_linked else ""
                        hidden = " [HIDDEN]" if hasattr(in_sock, 'hide') and in_sock.hide else ""
                        error_msg += f"\n     [{idx}] {in_sock.name} (type: {sock_type}){linked}{hidden}"
                
                connection_stats['failed_socket_not_found'] += 1
                failed_links.append(error_msg)
                
        except Exception as e:
            connection_stats['failed_other'] += 1
            failed_links.append(f"Link {i}: Exception - {str(e)}")
    
    # Report failed links
    if failed_links:
        print(f"[Material Generator] ⚠ {len(failed_links)} link(s) failed:")
        for fail in failed_links:
            print(f"  - {fail}")
    
    # =====================================================================
    # LINKING SUMMARY
    # =====================================================================
    print("\n" + "=" * 70)
    print("[Material Generator] 📊 LINKING SUMMARY")
    print("=" * 70)
    print(f"  Attempted: {connection_stats['attempted']}")
    print(f"  ✓ Successful: {connection_stats['successful']}")
    if connection_stats['failed_socket_not_found'] > 0:
        print(f"  ❌ Failed (socket not found): {connection_stats['failed_socket_not_found']}")
    if connection_stats['failed_incompatible'] > 0:
        print(f"  ❌ Failed (incompatible types): {connection_stats['failed_incompatible']}")
    if connection_stats['failed_other'] > 0:
        print(f"  ❌ Failed (other errors): {connection_stats['failed_other']}")
    
    success_rate = (connection_stats['successful'] / connection_stats['attempted'] * 100) if connection_stats['attempted'] > 0 else 0
    print(f"  Success Rate: {success_rate:.1f}%")
    print("=" * 70 + "\n")
    
    return success_count


def hide_unused_mix_sockets(node, data_type):
    """
    Hide Mix node sockets yang tidak relevan untuk data_type yang dipilih.
    Blender shows ALL 8 input sockets regardless of data_type, causing confusion.
    
    Args:
        node: Mix node
        data_type: Current data_type ('RGBA', 'FLOAT', 'VECTOR')
    """
    if node.bl_idname != 'ShaderNodeMix':
        return
    
    # Socket indices that should be VISIBLE for each data_type
    # CRITICAL FIX: Corrected socket indices for RGBA
    # Mix node socket layout:
    # [0] Factor (VALUE), [1] Factor (VECTOR)
    # [2] A (VALUE), [3] B (VALUE)
    # [4] A (VECTOR), [5] B (VECTOR)  
    # [6] A (RGBA), [7] B (RGBA)
    VISIBLE_SOCKETS = {
        'RGBA': [0, 6, 7],      # Factor[0], A[6] (RGBA), B[7] (RGBA)
        'FLOAT': [0, 2, 3],     # Factor[0], A[2] (VALUE), B[3] (VALUE)
        'VECTOR': [0, 4, 5],    # Factor[0], A[4] (VECTOR), B[5] (VECTOR)
    }
    
    if data_type not in VISIBLE_SOCKETS:
        return
    
    visible_indices = VISIBLE_SOCKETS[data_type]
    
    # Hide all input sockets EXCEPT the relevant ones
    for i, socket in enumerate(node.inputs):
        if i in visible_indices:
            socket.hide = False  # Show relevant sockets
        else:
            socket.hide = True   # Hide irrelevant sockets


def find_socket_for_mix_node(node, socket_name, socket_type="input"):
    """
    Find socket untuk Mix node.
    After data_type is set, Blender automatically shows/hides relevant sockets.
    We just need to find by name among visible sockets.
    
    Args:
        node: The Mix node
        socket_name: Name of socket to find ('Factor', 'Fac', 'A', 'B', 'Result', 'Color')
        socket_type: 'input' or 'output'
        
    Returns:
        Socket or None
    """
    if node.bl_idname != 'ShaderNodeMix':
        return None
    
    # CRITICAL FIX: Handle both old and new socket names with comprehensive aliases
    # Old AI might send: "Fac", "Color1", "Color2", "Color" (for output)
    # New sockets are: "Factor", "A", "B", "Result"
    
    socket_aliases = {
        # Input aliases
        "fac": ["Factor", "Fac"],
        "factor": ["Factor", "Fac"],
        "a": ["A"],
        "b": ["B"],
        "color1": ["A", "Color1"],  # Legacy MixRGB compatibility
        "color2": ["B", "Color2"],  # Legacy MixRGB compatibility
        # Output aliases
        "result": ["Result"],
        "color": ["Result", "Color"],  # Handle AI using "Color" for Mix output
    }
    
    # =====================================================================
    # CRITICAL FIX FOR OUTPUT SOCKETS: Mix node has 3 "Result" sockets!
    # They have the SAME NAME but DIFFERENT TYPES at different indices:
    # - Index 0: Result (VALUE) for data_type='FLOAT'
    # - Index 1: Result (VECTOR) for data_type='VECTOR'  
    # - Index 2: Result (RGBA) for data_type='RGBA'
    # =====================================================================
    if socket_type == "output" and socket_name.lower() in ["result", "color"]:
        if hasattr(node, 'data_type'):
            data_type = node.data_type
            # Map data_type to correct Result socket index
            RESULT_SOCKET_INDEX = {
                'FLOAT': 0,    # Result (VALUE)
                'VECTOR': 1,   # Result (VECTOR)
                'RGBA': 2,     # Result (RGBA)
            }
            
            result_index = RESULT_SOCKET_INDEX.get(data_type, 0)
            if result_index < len(node.outputs):
                result_socket = node.outputs[result_index]
                print(f"[Material Generator] ✓ Mix node output: selected Result socket index {result_index} for data_type='{data_type}'")
                return result_socket
            else:
                print(f"[Material Generator] ⚠️ Mix node: Result socket index {result_index} out of range")
        else:
            print(f"[Material Generator] ⚠️ Mix node missing data_type property, using first Result socket")
    
    # =====================================================================
    # CRITICAL FIX FOR INPUT SOCKETS: Mix node has multiple "A" and "B" sockets!
    # They have the SAME NAME but DIFFERENT TYPES at different indices:
    # A sockets: [2] A (VALUE), [4] A (VECTOR), [6] A (RGBA)
    # B sockets: [3] B (VALUE), [5] B (VECTOR), [7] B (RGBA)
    # =====================================================================
    if socket_type == "input" and socket_name.lower() in ["a", "b", "color1", "color2"]:
        if hasattr(node, 'data_type'):
            data_type = node.data_type
            
            # Determine if looking for A or B
            is_socket_a = socket_name.lower() in ["a", "color1"]
            
            # Map data_type to correct socket index
            SOCKET_A_INDEX = {
                'FLOAT': 2,    # A (VALUE)
                'VECTOR': 4,   # A (VECTOR)
                'RGBA': 6,     # A (RGBA)
            }
            
            SOCKET_B_INDEX = {
                'FLOAT': 3,    # B (VALUE)
                'VECTOR': 5,   # B (VECTOR)
                'RGBA': 7,     # B (RGBA)
            }
            
            socket_index_map = SOCKET_A_INDEX if is_socket_a else SOCKET_B_INDEX
            socket_index = socket_index_map.get(data_type)
            
            if socket_index is not None and socket_index < len(node.inputs):
                target_socket = node.inputs[socket_index]
                socket_letter = "A" if is_socket_a else "B"
                print(f"[Material Generator] ✓ Mix node input: selected {socket_letter} socket index {socket_index} ({target_socket.type}) for data_type='{data_type}'")
                return target_socket
            else:
                print(f"[Material Generator] ⚠️ Mix node: socket index {socket_index} out of range")
        else:
            print(f"[Material Generator] ⚠️ Mix node missing data_type property")
    
    # Normalize socket name and get search candidates
    socket_name_lower = socket_name.lower()
    search_names = socket_aliases.get(socket_name_lower, [socket_name])
    
    sockets = node.inputs if socket_type == "input" else node.outputs
    
    # Try each alias in order of priority
    for name in search_names:
        for socket in sockets:
            if socket.name == name and not socket.hide:
                if socket_type == "input":
                    # For inputs, prefer unconnected sockets
                    if not socket.is_linked:
                        return socket
                else:
                    # For outputs, return first match
                    return socket
        
        # If all matching sockets are connected, return first match
        for socket in sockets:
            if socket.name == name and not socket.hide:
                return socket
    
    # Enhanced logging if socket not found
    print(f"[Material Generator] ⚠ Mix node socket '{socket_name}' not found")
    print(f"  Tried aliases: {search_names}")
    print(f"  Mix node data_type: {node.data_type if hasattr(node, 'data_type') else 'N/A'}")
    print(f"  Available {socket_type} sockets:")
    for socket in sockets:
        linked_status = "linked" if hasattr(socket, 'is_linked') and socket.is_linked else "unlinked"
        hidden_status = "hidden" if socket.hide else "visible"
        print(f"    - {socket.name} ({linked_status}, {hidden_status})")
    
    return None


def find_socket_smart(sockets, socket_name, socket_type="", node=None):
    """
    Find socket dengan flexible matching DAN handling untuk same-named sockets
    (e.g., Add Shader has two "Shader" inputs, Mix has multiple "A"/"B" inputs)
    
    Args:
        sockets: List of sockets to search
        socket_name: Name to search for
        socket_type: "input" or "output" for better error messages
        node: The node object (needed for Mix node special handling)
        
    Returns:
        Socket object atau None
    """
    # SPECIAL HANDLING: Mix nodes have multiple sockets with same names
    # Use hardcoded indices based on data_type
    if node and node.bl_idname == 'ShaderNodeMix':
        mix_socket = find_socket_for_mix_node(node, socket_name, socket_type)
        if mix_socket:
            return mix_socket
        # else: fall through to general search
    
    # Collect all matching sockets by name (exact match first)
    matching_sockets = []
    
    # Try exact match first
    for socket in sockets:
        if socket.name == socket_name:
            matching_sockets.append(socket)
    
    # If no exact match, try case-insensitive
    if not matching_sockets:
        socket_name_lower = socket_name.lower()
        for socket in sockets:
            if socket.name.lower() == socket_name_lower:
                matching_sockets.append(socket)
    
    # If still no match, try partial match
    if not matching_sockets:
        for socket in sockets:
            if socket_name_lower in socket.name.lower() or socket.name.lower() in socket_name_lower:
                matching_sockets.append(socket)
    
    # If still no match, try aliases
    if not matching_sockets:
        aliases = {
            # Output socket aliases
            "bsdf": ["BSDF", "Shader"],
            "shader": ["BSDF", "Shader"],
            "emission": ["Emission", "Shader"],
            "color": ["Color", "Result", "Value", "Fac"],  # EXPANDED: Added Result for Mix node output
            "fac": ["Fac", "Factor", "Value"],  # EXPANDED: Added Factor for Mix input
            "factor": ["Factor", "Fac"],
            "value": ["Value", "Fac", "Result"],  # EXPANDED: Handle Math vs Mix outputs
            "vector": ["Vector"],
            "normal": ["Normal"],
            "result": ["Result", "Value", "Color"],  # EXPANDED: Mix uses 'Result', added Color as fallback
            "alpha": ["Alpha"],  # NEW: For ColorRamp second output
            
            # Input socket aliases  
            "surface": ["Surface"],
            "base color": ["Base Color", "Color"],
            "base_color": ["Base Color", "Color"],
            "roughness": ["Roughness"],
            "metallic": ["Metallic"],
            "normal": ["Normal"],
            "height": ["Height"],
            "shader": ["Shader", "BSDF"],
            # Mix node aliases (ShaderNodeMix new vs ShaderNodeMixRGB legacy)
            "color1": ["Color1", "A"],  # Legacy MixRGB uses Color1, new Mix uses A
            "color2": ["Color2", "B"],  # Legacy MixRGB uses Color2, new Mix uses B
            "a": ["A", "Color1"],
            "b": ["B", "Color2"],
            "fac": ["Fac", "Factor"],  # CRITICAL: Both directions for Mix node Factor input
        }
        
        socket_name_key = socket_name.lower()
        if socket_name_key in aliases:
            for alias in aliases[socket_name_key]:
                for socket in sockets:
                    if socket.name == alias:
                        matching_sockets.append(socket)
    
    # If we found matching sockets, prioritize unconnected sockets for inputs
    # but ALLOW connected sockets as fallback (Blender will replace connections)
    if matching_sockets:
        # For input sockets: prefer unconnected, but accept connected as fallback
        if socket_type == "input":
            # First, try to find an unconnected socket
            for socket in matching_sockets:
                if not socket.is_linked:
                    return socket
            # If all are connected, return first one (Blender will replace the connection)
            return matching_sockets[0]
        else:
            # Output sockets: can have multiple connections, just return first match
            return matching_sockets[0]
    
    # Enhanced Debug: print detailed socket information
    print(f"[Material Generator] ❌ SOCKET NOT FOUND")
    print(f"  Looking for: '{socket_name}' ({socket_type})")
    
    if node:
        print(f"  Node: {node.name} (type: {node.bl_idname})")
        
        # For Mix nodes, show data_type which affects available sockets
        if node.bl_idname == 'ShaderNodeMix' and hasattr(node, 'data_type'):
            print(f"  Mix node data_type: {node.data_type}")
    
    print(f"  Available {socket_type} sockets ({len(sockets)} total):")
    for i, s in enumerate(sockets):
        # Show socket details: index, name, type, and linked status
        linked_status = ""
        if hasattr(s, 'is_linked'):
            linked_status = " [LINKED]" if s.is_linked else " [unlinked]"
        
        hidden_status = ""
        if hasattr(s, 'hide') and s.hide:
            hidden_status = " [HIDDEN]"
        
        socket_type_info = f" (type: {s.type})" if hasattr(s, 'type') else ""
        print(f"    [{i}] {s.name}{socket_type_info}{linked_status}{hidden_status}")
    
    # Try to suggest alternatives based on partial matching
    suggestions = []
    socket_name_lower = socket_name.lower()
    for s in sockets:
        if socket_name_lower in s.name.lower() or s.name.lower() in socket_name_lower:
            if not hasattr(s, 'hide') or not s.hide:  # Don't suggest hidden sockets
                suggestions.append(s.name)
    
    if suggestions:
        print(f"  💡 Suggestions: {', '.join(suggestions)}")
    
    return None


# FUNGSI INI DIHAPUS - Diganti dengan find_socket_smart yang lebih lengkap
# find_socket() sudah diganti dengan find_socket_smart() yang menangani:
# - Mix nodes dengan multiple same-named sockets
# - Flexible socket matching dengan aliases
# - Better handling untuk connected vs unconnected sockets
# 
# Jika ada kode yang masih memanggil find_socket(), gunakan find_socket_smart() sebagai gantinya


def modify_existing_material(material, modifications_config):
    """
    Modify material yang sudah ada berdasarkan config
    
    Args:
        material: Existing Blender material
        modifications_config (dict): Modifications dari AI
        
    Returns:
        Material: Modified material
    """
    # Untuk sekarang, kita replace semua nodes
    # Future: bisa implement smart modification (add/remove specific nodes)
    return create_material_from_config(modifications_config, assign_to_active=False)


def update_material_from_config(material, new_config, merge_with_existing=True):
    """
    Update existing material dengan config baru, bisa merge dengan node yang ada
    
    Args:
        material: Blender material yang akan diupdate
        new_config (dict): Material configuration dari AI
        merge_with_existing (bool): Jika True, merge dengan nodes yang ada. Jika False, replace semua.
        
    Returns:
        Material: Updated material
    """
    try:
        if not merge_with_existing:
            # Simple replace - clear and rebuild
            return create_material_from_config(new_config, assign_to_active=False)
        
        # MERGE MODE: Integrate new nodes with existing ones
        print(f"[Material Generator] Merging with existing material: {material.name}")
        
        # Get node tree
        node_tree = material.node_tree
        existing_nodes = list(node_tree.nodes)  # Copy list
        
        print(f"[Material Generator] Existing nodes: {len(existing_nodes)}")
        print(f"[Material Generator] New config has {len(new_config.get('nodes', []))} nodes")
        
        # Strategy: AI should return ALL nodes (existing + new)
        # We'll replace all nodes but try to preserve existing ones by matching
        
        # Clear all nodes (kita akan rebuild semuanya)
        node_tree.nodes.clear()
        
        # Create all nodes from new config
        node_objects = []
        for i, node_config in enumerate(new_config['nodes']):
            node = create_node(material, node_config)
            if node:
                node_objects.append(node)
            else:
                print(f"[Material Generator] Failed to create node {i}: {node_config.get('type')}")
        
        # Create all links
        links_config = new_config.get('links', [])
        success_links = link_nodes(material, links_config, node_objects)
        print(f"[Material Generator] Updated material: {len(node_objects)} nodes, {success_links} links")
        
        # Auto-arrange nodes untuk readability berdasarkan graph connectivity
        arrange_nodes(material, links_config, node_objects)
        
        return material
        
    except Exception as e:
        print(f"[Material Generator] Error updating material: {str(e)}")
        import traceback
        traceback.print_exc()
        return None


def build_node_graph(links_config, node_count):
    """
    Build graph structure dari link configuration.
    
    Args:
        links_config: List of link configurations
        node_count: Total jumlah nodes
        
    Returns:
        dict: {
            'children': {node_idx: [child_indices]},
            'parents': {node_idx: [parent_indices]},
            'roots': [root_node_indices],
            'leaves': [leaf_node_indices]
        }
    """
    # Initialize graph structure
    children = {i: [] for i in range(node_count)}
    parents = {i: [] for i in range(node_count)}
    
    # Build adjacency lists
    for link in links_config:
        from_idx = link['from_node']
        to_idx = link['to_node']
        
        # Validate indices
        if from_idx < node_count and to_idx < node_count:
            children[from_idx].append(to_idx)
            parents[to_idx].append(from_idx)
    
    # Find root nodes (tanpa parent/input)
    roots = [i for i in range(node_count) if len(parents[i]) == 0]
    
    # Find leaf nodes (tanpa children/output)
    leaves = [i for i in range(node_count) if len(children[i]) == 0]
    
    return {
        'children': children,
        'parents': parents,
        'roots': roots,
        'leaves': leaves
    }


def calculate_node_depths(graph, node_count):
    """
    Calculate depth level untuk setiap node menggunakan BFS dari root nodes.
    Depth menunjukkan jarak dari root node (source).
    
    Args:
        graph: Graph structure dari build_node_graph()
        node_count: Total jumlah nodes
        
    Returns:
        dict: {node_idx: depth_level}
    """
    from collections import deque
    
    depths = {}
    visited = set()
    queue = deque()
    
    # Start BFS dari semua root nodes dengan depth 0
    for root_idx in graph['roots']:
        queue.append((root_idx, 0))
        depths[root_idx] = 0
        visited.add(root_idx)
    
    # BFS traversal
    while queue:
        node_idx, depth = queue.popleft()
        
        # Visit all children
        for child_idx in graph['children'][node_idx]:
            if child_idx not in visited:
                visited.add(child_idx)
                depths[child_idx] = depth + 1
                queue.append((child_idx, depth + 1))
            else:
                # Node sudah dikunjungi, tapi mungkin ada path yang lebih panjang
                # Update depth jika path baru lebih panjang (untuk handle multiple paths)
                if depth + 1 > depths.get(child_idx, 0):
                    depths[child_idx] = depth + 1
                    queue.append((child_idx, depth + 1))
    
    # Handle nodes yang tidak terhubung (isolated nodes)
    for i in range(node_count):
        if i not in depths:
            depths[i] = 0  # Put isolated nodes at depth 0
    
    return depths


def arrange_nodes_by_graph(material, links_config, node_objects):
    """
    Arrange nodes berdasarkan graph connectivity (kiri ke kanan mengikuti koneksi).
    Menggunakan depth-based positioning dari hasil BFS.
    
    Args:
        material: Blender material
        links_config: List of link configurations
        node_objects: List of created node objects
    """
    try:
        if not node_objects or not links_config:
            print("[Material Generator] ⚠ Cannot arrange nodes: no nodes or links")
            return
        
        # Build graph structure
        node_count = len(node_objects)
        graph = build_node_graph(links_config, node_count)
        
        print(f"[Material Generator] 📊 Graph Analysis:")
        print(f"  Root nodes (depth 0): {len(graph['roots'])}")
        print(f"  Leaf nodes (outputs): {len(graph['leaves'])}")
        
        # Calculate depths
        depths = calculate_node_depths(graph, node_count)
        
        # Group nodes by depth
        nodes_by_depth = {}
        max_depth = 0
        for node_idx, depth in depths.items():
            if depth not in nodes_by_depth:
                nodes_by_depth[depth] = []
            nodes_by_depth[depth].append(node_idx)
            max_depth = max(max_depth, depth)
        
        print(f"  Maximum depth: {max_depth}")
        for depth in range(max_depth + 1):
            count = len(nodes_by_depth.get(depth, []))
            if count > 0:
                print(f"  Depth {depth}: {count} node(s)")
        
        # Spacing configuration
        x_spacing = 300  # Horizontal spacing between depth levels
        y_spacing = 250  # Vertical spacing between nodes in same depth
        
        # Position nodes berdasarkan depth
        for depth in range(max_depth + 1):
            if depth not in nodes_by_depth:
                continue
            
            nodes_at_depth = nodes_by_depth[depth]
            num_nodes = len(nodes_at_depth)
            
            # Calculate X position (same for all nodes at this depth)
            x_pos = depth * x_spacing
            
            # Calculate Y positions (centered and staggered vertically)
            # Start from center and go up/down
            y_start = -(num_nodes - 1) * y_spacing / 2
            
            for i, node_idx in enumerate(nodes_at_depth):
                if node_idx < len(node_objects):
                    node = node_objects[node_idx]
                    y_pos = y_start + i * y_spacing
                    node.location = (x_pos, y_pos)
        
        print(f"[Material Generator] ✓ Nodes arranged horizontally by depth (left to right)")
        
    except Exception as e:
        print(f"[Material Generator] Error in graph-based arrangement: {str(e)}")
        import traceback
        traceback.print_exc()


def arrange_nodes(material, links_config=None, node_objects=None):
    """
    Auto-arrange nodes untuk better readability.
    
    Jika links_config dan node_objects tersedia, gunakan graph-based arrangement
    yang mengatur node dari kiri ke kanan mengikuti alur koneksi.
    
    Jika tidak tersedia, fallback ke simple grid layout untuk nodes yang overlap di [0, 0]
    
    Args:
        material: Blender material
        links_config: (Optional) List of link configurations untuk graph-based arrangement
        node_objects: (Optional) List of node objects untuk graph-based arrangement
    """
    try:
        # PRIORITAS 1: Graph-based arrangement jika data tersedia
        if links_config is not None and node_objects is not None:
            print("[Material Generator] 📐 Using graph-based node arrangement...")
            arrange_nodes_by_graph(material, links_config, node_objects)
            return
        
        # PRIORITAS 2: Fallback ke grid layout (backward compatibility)
        print("[Material Generator] 📐 Using grid-based node arrangement (fallback)...")
        nodes = material.node_tree.nodes
        
        # Check if there are nodes that need arrangement (all at [0, 0])
        nodes_at_origin = [n for n in nodes if n.location[0] == 0 and n.location[1] == 0]
        
        if len(nodes_at_origin) > 1:
            print(f"[Material Generator] Auto-arranging {len(nodes_at_origin)} overlapping nodes...")
            
            # Simple grid layout
            x_spacing = 250
            y_spacing = 300
            nodes_per_row = 5
            
            for i, node in enumerate(nodes_at_origin):
                col = i % nodes_per_row
                row = i // nodes_per_row
                node.location = (col * x_spacing, -row * y_spacing)
            
            print(f"[Material Generator] ✓ Nodes arranged in {((len(nodes_at_origin)-1)//nodes_per_row)+1} row(s)")
        
    except Exception as e:
        print(f"[Material Generator] Error arranging nodes: {str(e)}")
        import traceback
        traceback.print_exc()



def get_material_preview_setup():
    """
    Setup material preview (untuk testing)
    Create simple sphere dengan material
    """
    # Check if preview sphere exists
    if "MaterialPreview_Sphere" in bpy.data.objects:
        return bpy.data.objects["MaterialPreview_Sphere"]
    
    # Create preview sphere
    bpy.ops.mesh.primitive_uv_sphere_add(radius=1, location=(0, 0, 0))
    sphere = bpy.context.active_object
    sphere.name = "MaterialPreview_Sphere"
    
    return sphere
