"""
Blender AI Procedural Material Generator
Operators - Handle user actions
"""

import bpy
from bpy.types import Operator
from bpy.props import StringProperty, BoolProperty
from . import ai_connector
from . import material_generator
from . import utils


class MATERIAL_OT_generate_ai(Operator):
    """Generate material baru dari AI prompt"""
    bl_idname = "material.generate_ai"
    bl_label = "Generate Material"
    bl_options = {'REGISTER', 'UNDO'}
    
    def execute(self, context):
        scene = context.scene
        props = scene.ai_material_props
        
        prompt = props.prompt.strip()
        
        if not prompt:
            self.report({'ERROR'}, "Please enter a prompt")
            return {'CANCELLED'}
        
        # Check API ready
        if not ai_connector.is_api_ready():
            self.report({'ERROR'}, "API not initialized. Please set API key in settings.")
            return {'CANCELLED'}
        
        # Set status
        props.is_generating = True
        props.status_message = "Generating material..."
        
        # Force UI update
        context.area.tag_redraw()
        
        # Call AI
        current_model = ai_connector.get_current_model_name()
        print(f"[Operator] Generating material for: {prompt}")
        print(f"[Operator] Starting with model: {current_model}")
        result = ai_connector.generate_material_config(
            prompt,
            prompt_history=props.prompt_history_list
        )
        
        # Handle tuple response (config, error_type, user_message)
        config = None
        error_type = None
        user_message = None
        if isinstance(result, tuple):
            if len(result) == 3:
                config, error_type, user_message = result
            elif len(result) == 2:
                config, error_type = result
            else:
                config = result[0] if result else None
        else:
            config = result
        
        if config:
            # Create material
            material = material_generator.create_material_from_config(config)
            
            if material:
                # Get model yang berhasil
                successful_model = ai_connector.get_current_model_name()
                
                # Add to history
                props.add_to_history(prompt)
                props.last_generated_material = material.name
                props.status_message = f"Created: {material.name} (using {successful_model})"
                
                # Set workflow state
                props.has_generated = True
                props.current_model = successful_model
                
                self.report({'INFO'}, f"Material '{material.name}' created successfully with {successful_model}")
                
                # Clear prompt untuk next input
                # props.prompt = ""  # Optional: keep or clear
                
                props.is_generating = False
                return {'FINISHED'}
        
        # Generation failed - show error message
        props.is_generating = False
        
        # Use user_message from ai_connector if available
        if user_message:
            self.report({'ERROR'}, user_message)
            props.status_message = user_message[:50] + "..." if len(user_message) > 50 else user_message
        elif error_type == 'quota_exceeded':
            msg = "Quota exceeded. Please try another model or wait."
            self.report({'ERROR'}, msg)
            props.status_message = msg
        elif error_type == 'unauthorized':
            msg = "Model requires paid tier. Please upgrade API key."
            self.report({'ERROR'}, msg)
            props.status_message = msg
        else:
            self.report({'ERROR'}, "Failed to generate material")
            props.status_message = "Generation failed"
        
        return {'CANCELLED'}


class MATERIAL_OT_modify_ai(Operator):
    """Modify material existing dengan AI prompt"""
    bl_idname = "material.modify_ai"
    bl_label = "Modify Material"
    bl_options = {'REGISTER', 'UNDO'}
    
    def execute(self, context):
        scene = context.scene
        props = scene.ai_material_props
        
        prompt = props.prompt.strip()
        
        if not prompt:
            self.report({'ERROR'}, "Please enter a modification prompt")
            return {'CANCELLED'}
        
        # Check API ready
        if not ai_connector.is_api_ready():
            self.report({'ERROR'}, "API not initialized")
            return {'CANCELLED'}
        
        # Get current material
        obj = context.active_object
        if not obj or not obj.active_material:
            self.report({'ERROR'}, "No active material to modify")
            return {'CANCELLED'}
        
        current_material = obj.active_material
        
        # Get current material config
        current_config = utils.get_active_material_config()
        
        if not current_config:
            self.report({'ERROR'}, "Failed to read current material configuration")
            return {'CANCELLED'}
        
        # Set status
        props.is_generating = True
        props.status_message = "Modifying material..."
        context.area.tag_redraw()
        
        # Call AI dengan current material config
        current_model = ai_connector.get_current_model_name()
        print(f"[Operator] Modifying material: {prompt}")
        print(f"[Operator] Current material has {len(current_config['nodes'])} nodes")
        print(f"[Operator] Starting with model: {current_model}")
        result = ai_connector.generate_material_config(
            prompt,
            prompt_history=props.prompt_history_list,
            current_material_config=current_config  # Pass actual config, not just flag
        )
        
        
        # Handle tuple response (config, error_type, user_message)
        config = None
        error_type = None
        user_message = None
        if isinstance(result, tuple):
            if len(result) == 3:
                config, error_type, user_message = result
            elif len(result) == 2:
                config, error_type = result
            else:
                config = result[0] if result else None
        else:
            config = result
        
        if config:
            # Update existing material instead of creating new one
            material = material_generator.update_material_from_config(
                current_material, 
                config, 
                merge_with_existing=True
            )
            
            if material:
                # Get model yang berhasil
                successful_model = ai_connector.get_current_model_name()
                
                # Add to history
                props.add_to_history(prompt)
                props.status_message = f"Modified: {material.name} (using {successful_model})"
                
                # Update current model
                props.current_model = successful_model
                
                self.report({'INFO'}, f"Material modified successfully with {successful_model}")
                props.is_generating = False
                return {'FINISHED'}
        
        # Modification failed - show error message
        props.is_generating = False
        
        # Use user_message from ai_connector if available
        if user_message:
            self.report({'ERROR'}, user_message)
            props.status_message = user_message[:50] + "..." if len(user_message) > 50 else user_message
        elif error_type == 'quota_exceeded':
            msg = "Quota exceeded. Please try another model or wait."
            self.report({'ERROR'}, msg)
            props.status_message = msg
        elif error_type == 'unauthorized':
            msg = "Model requires paid tier. Please upgrade API key."
            self.report({'ERROR'}, msg)
            props.status_message = msg
        else:
            self.report({'ERROR'}, "Failed to modify material")
            props.status_message = "Modification failed"
        
        return {'CANCELLED'}


class MATERIAL_OT_clear_history(Operator):
    """Clear prompt history"""
    bl_idname = "material.clear_history"
    bl_label = "Clear History"
    
    def execute(self, context):
        props = context.scene.ai_material_props
        props.clear_history()
        props.status_message = "History cleared"
        self.report({'INFO'}, "Prompt history cleared")
        return {'FINISHED'}


class MATERIAL_OT_start_over(Operator):
    """Start over - Reset workflow dan generate material baru"""
    bl_idname = "material.start_over"
    bl_label = "Start Over"
    bl_options = {'REGISTER', 'UNDO'}
    
    def execute(self, context):
        scene = context.scene
        props = scene.ai_material_props
        
        prompt = props.prompt.strip()
        
        if not prompt:
            self.report({'ERROR'}, "Please enter a prompt")
            return {'CANCELLED'}
        
        # Check API ready
        if not ai_connector.is_api_ready():
            self.report({'ERROR'}, "API not initialized. Please set API key in settings.")
            return {'CANCELLED'}
        
        # Reset workflow state
        props.reset_workflow()
        
        # Set status
        props.is_generating = True
        props.status_message = "Generating new material..."
        
        # Force UI update
        context.area.tag_redraw()
        
        # Get current active material (jika ada)
        obj = context.active_object
        current_material = None
        if obj and obj.active_material:
            current_material = obj.active_material
        
        # Call AI untuk generate material baru
        current_model = ai_connector.get_current_model_name()
        print(f"[Start Over] Generating new material for: {prompt}")
        print(f"[Start Over] Starting with model: {current_model}")
        result = ai_connector.generate_material_config(
            prompt,
            prompt_history=[]  # Empty history karena start over
        )
        
        # Handle tuple response (config, error_type, user_message)
        config = None
        error_type = None
        user_message = None
        if isinstance(result, tuple):
            if len(result) == 3:
                config, error_type, user_message = result
            elif len(result) == 2:
                config, error_type = result
            else:
                config = result[0] if result else None
        else:
            config = result
        
        if config:
            # Jika ada material aktif, update material tersebut. Jika tidak, create new
            if current_material:
                material = material_generator.update_material_from_config(
                    current_material, 
                    config, 
                    merge_with_existing=False  # Replace completely
                )
            else:
                material = material_generator.create_material_from_config(config)
            
            if material:
                # Get model yang berhasil
                successful_model = ai_connector.get_current_model_name()
                
                # Add to history
                props.add_to_history(prompt)
                props.last_generated_material = material.name
                props.status_message = f"New material: {material.name} (using {successful_model})"
                
                # Set workflow state
                props.has_generated = True
                props.current_model = successful_model
                
                self.report({'INFO'}, f"Started over with new material '{material.name}' using {successful_model}")
                
                props.is_generating = False
                return {'FINISHED'}
        
        # Generation failed - show error message
        props.is_generating = False
        
        # Use user_message from ai_connector if available
        if user_message:
            self.report({'ERROR'}, user_message)
            props.status_message = user_message[:50] + "..." if len(user_message) > 50 else user_message
        elif error_type == 'quota_exceeded':
            msg = "Quota exceeded. Please try another model or wait."
            self.report({'ERROR'}, msg)
            props.status_message = msg
        elif error_type == 'unauthorized':
            msg = "Model requires paid tier. Please upgrade API key."
            self.report({'ERROR'}, msg)
            props.status_message = msg
        else:
            self.report({'ERROR'}, "Failed to generate material")
            props.status_message = "Generation failed"
        
        return {'CANCELLED'}



class MATERIAL_OT_set_api_key(Operator):
    """Initialize AI API dengan API key"""
    bl_idname = "material.set_api_key"
    bl_label = "Set API Key"
    
    def execute(self, context):
        props = context.scene.ai_material_props
        
        if not props.api_key:
            self.report({'ERROR'}, "API Key cannot be empty")
            return {'CANCELLED'}
        
        # Initialize API with user's preferred model
        success = ai_connector.init_api(props.api_key, props.preferred_model)
        
        if success:
            props.api_initialized = True
            # Update current model display
            current_model = ai_connector.get_current_model_name()
            if current_model:
                props.current_model = current_model
            self.report({'INFO'}, f"API initialized with {props.current_model}")
            props.status_message = f"API initialized with {props.current_model}" # Added this line to match original logic
            return {'FINISHED'}
        else:
            props.api_initialized = False
            props.current_model = ""
            props.status_message = "API initialization failed"
            self.report({'ERROR'}, "Failed to initialize API. Check console for details.")
            return {'CANCELLED'}




# Registrasi classes
classes = (
    MATERIAL_OT_generate_ai,
    MATERIAL_OT_modify_ai,
    MATERIAL_OT_clear_history,
    MATERIAL_OT_start_over,
    MATERIAL_OT_set_api_key,
)


def register():
    for cls in classes:
        bpy.utils.register_class(cls)


def unregister():
    for cls in reversed(classes):
        bpy.utils.unregister_class(cls)
