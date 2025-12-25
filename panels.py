"""
Blender AI Procedural Material Generator
UI Panels - User interface di Shader Editor
"""

import bpy
from bpy.types import Panel
from . import prompt_templates


class MATERIAL_PT_ai_generator(Panel):
    """Main panel untuk AI Material Generator"""
    bl_label = "AI Material Generator"
    bl_idname = "MATERIAL_PT_ai_generator"
    bl_space_type = 'NODE_EDITOR'
    bl_region_type = 'UI'
    bl_category = 'AI Material'
    bl_context = "shader"
    
    def draw(self, context):
        layout = self.layout
        scene = context.scene
        props = scene.ai_material_props
        
        # Header
        box = layout.box()
        box.label(text="Procedural Material from AI", icon='SHADING_TEXTURE')
        
        # API Status
        if props.api_initialized:
            box.label(text="✓ API Ready", icon='CHECKMARK')
        else:
            box.label(text="⚠ API Not Initialized", icon='ERROR')
        
        # Prompt input
        col = layout.column(align=True)
        col.label(text="Describe Material:")
        col.prop(props, "prompt", text="")
        
        # Generate/Modify buttons - Dinamis berdasarkan workflow state
        if props.is_generating:
            # Saat generating, disable semua tombol
            row = layout.row(align=True)
            row.scale_y = 1.5
            row.enabled = False
            row.operator("material.generate_ai", text="Generating...", icon='TIME')
        elif not props.has_generated:
            # State awal: Tampilkan tombol Generate saja
            row = layout.row(align=True)
            row.scale_y = 1.5
            row.operator("material.generate_ai", text="Generate", icon='ADD')
        else:
            # Setelah generate: Tampilkan tombol Modify sebagai tombol utama
            row = layout.row(align=True)
            row.scale_y = 1.5
            row.operator("material.modify_ai", text="Modify", icon='MODIFIER')
            
            # Tombol Start Over di row terpisah
            row = layout.row(align=True)
            row.scale_y = 1.2
            row.operator("material.start_over", text="Start Over", icon='FILE_REFRESH')
        
        # Status message
        if props.status_message:
            box = layout.box()
            box.label(text=props.status_message, icon='INFO')
        
        # Prompt history
        if len(props.prompt_history_list) > 0:
            box = layout.box()
            box.label(text="History:", icon='TIME')
            
            for i, hist_prompt in enumerate(reversed(props.prompt_history_list[-5:])):
                box.label(text=f"  {i+1}. {hist_prompt[:40]}...")
            
            box.operator("material.clear_history", text="Clear History", icon='TRASH')


class MATERIAL_PT_ai_settings(Panel):
    """Settings panel untuk API key dan preferences"""
    bl_label = "Settings"
    bl_idname = "MATERIAL_PT_ai_settings"
    bl_space_type = 'NODE_EDITOR'
    bl_region_type = 'UI'
    bl_category = 'AI Material'
    bl_context = "shader"
    bl_parent_id = "MATERIAL_PT_ai_generator"
    bl_options = {'DEFAULT_CLOSED'}
    
    def draw(self, context):
        layout = self.layout
        scene = context.scene
        props = scene.ai_material_props
        
        # ============================================================
        # SECTION 1: API SETUP
        # ============================================================
        box = layout.box()
        box.label(text="API Configuration", icon='PREFERENCES')
        
        col = box.column(align=True)
        col.label(text="Google Gemini API Key:")
        col.prop(props, "api_key", text="")
        
        # Initialize button
        row = box.row()
        row.scale_y = 1.3
        if props.api_initialized:
            row.operator("material.set_api_key", text="Reconnect API", icon='FILE_REFRESH')
        else:
            row.operator("material.set_api_key", text="Initialize API", icon='PLUGIN')
        
        # Info link
        info_box = box.box()
        info_box.scale_y = 0.7
        col = info_box.column(align=True)
        col.label(text="Get Free API Key:", icon='URL')
        col.label(text="ai.google.dev")
        
        layout.separator()
        
        # ============================================================
        # SECTION 2: MODEL SELECTION (only if API initialized)
        # ============================================================
        if props.api_initialized:
            box = layout.box()
            box.label(text="Model Selection", icon='SETTINGS')
            
            # Current model info
            if props.current_model != "":
                info_box = box.box()
                info_box.label(text="Currently Active:", icon='CHECKMARK')
                row = info_box.row()
                row.label(text=f"  {props.current_model}")
            
            box.separator(factor=0.5)
            
            # Model selector
            col = box.column(align=True)
            col.label(text="Choose Model:")
            col.prop(props, "preferred_model", text="")
            
            # Info box untuk model requirements
            info_box = box.box()
            info_box.scale_y = 0.7
            if props.preferred_model == 'gemini-3-pro-preview':
                info_box.label(text="💰 Requires paid tier API key", icon='ERROR')
                info_box.label(text="   (Preview model)", icon='NONE')
            elif props.preferred_model == 'gemini-3-flash-preview':
                info_box.label(text="💰 Requires paid tier API key", icon='ERROR')
                info_box.label(text="   (Preview model)", icon='NONE')
            elif props.preferred_model == 'gemini-2.5-pro':
                info_box.label(text="💰 Requires paid tier API key", icon='ERROR')
            else:  # gemini-2.5-flash
                info_box.label(text="✓ Free tier - Recommended", icon='CHECKMARK')
            
            layout.separator()
        
        # ============================================================
        # SECTION 3: ADDITIONAL SETTINGS
        # ============================================================
        layout.separator()
        layout.prop(props, "auto_assign", text="Auto-assign to selected")




class MATERIAL_PT_ai_examples(Panel):
    """Examples panel untuk show example prompts"""
    bl_label = "Example Prompts"
    bl_idname = "MATERIAL_PT_ai_examples"
    bl_space_type = 'NODE_EDITOR'
    bl_region_type = 'UI'
    bl_category = 'AI Material'
    bl_context = "shader"
    bl_parent_id = "MATERIAL_PT_ai_generator"
    bl_options = {'DEFAULT_CLOSED'}
    
    def draw(self, context):
        layout = self.layout
        
        layout.label(text="Try these prompts:", icon='BOOKMARKS')
        
        # Display example prompts
        for example in prompt_templates.EXAMPLE_PROMPTS:
            box = layout.box()
            box.label(text=f"• {example}")


# Callback function untuk auto-reconnect saat model diubah
def on_model_change(self, context):
    """
    Callback yang dipanggil saat preferred_model diubah.
    Otomatis reconnect API dengan model baru.
    """
    props = context.scene.ai_material_props
    
    # Hanya reconnect jika API sudah initialized sebelumnya
    if props.api_initialized and props.api_key:
        print(f"[Panel] Model changed to: {props.preferred_model}")
        print(f"[Panel] Auto-reconnecting API...")
        
        # Import di sini untuk avoid circular import
        from . import ai_connector
        
        # Reconnect dengan model baru
        success = ai_connector.init_api(props.api_key, props.preferred_model)
        
        if success:
            # Update current model display
            current_model = ai_connector.get_current_model_name()
            if current_model:
                props.current_model = current_model
                props.status_message = f"Switched to {current_model}"
                print(f"[Panel] ✓ Successfully switched to: {current_model}")
        else:
            # Reconnect failed - show error
            props.status_message = f"Failed to switch to {props.preferred_model}"
            print(f"[Panel] ✗ Failed to switch model")


# Property group untuk store addon state
class AIMaterialProperties(bpy.types.PropertyGroup):
    prompt: bpy.props.StringProperty(
        name="Prompt",
        description="Describe the material you want to create",
        default=""
    )
    
    api_key: bpy.props.StringProperty(
        name="API Key",
        description="Google Gemini API Key",
        default="",
        subtype='PASSWORD'
    )
    
    api_initialized: bpy.props.BoolProperty(
        name="API Initialized",
        description="Whether API is initialized",
        default=False
    )
    
    is_generating: bpy.props.BoolProperty(
        name="Is Generating",
        description="Whether currently generating material",
        default=False
    )
    
    status_message: bpy.props.StringProperty(
        name="Status Message",
        description="Current status message",
        default=""
    )
    
    last_generated_material: bpy.props.StringProperty(
        name="Last Generated Material",
        description="Name of last generated material",
        default=""
    )
    
    auto_assign: bpy.props.BoolProperty(
        name="Auto Assign",
        description="Automatically assign generated material to selected object",
        default=True
    )
    
    has_generated: bpy.props.BoolProperty(
        name="Has Generated",
        description="Whether user has generated material at least once",
        default=False
    )
    
    current_model: bpy.props.StringProperty(
        name="Current Model",
        description="Currently active AI model",
        default=""
    )
    
    preferred_model: bpy.props.EnumProperty(
        name="Preferred Model",
        description="Choose which AI model to use for generation",
        items=[
            ('gemini-3-pro-preview', 'Gemini 3 Pro 💰', 'Requires paid tier', 'FUND', 0),
            ('gemini-3-flash-preview', 'Gemini 3 Flash 💰', 'Requires paid tier', 'FUND', 1),
            ('gemini-2.5-pro', 'Gemini 2.5 Pro 💰', 'Requires paid tier', 'FUND', 2),
            ('gemini-2.5-flash', 'Gemini 2.5 Flash ✓', 'Free tier - Recommended', 'CHECKMARK', 3),
        ],
        default='gemini-2.5-flash',
        update=on_model_change  # Callback untuk auto-reconnect!
    )
    
    # Simple string untuk store history (comma-separated)
    prompt_history_internal: bpy.props.StringProperty(
        name="Prompt History Internal",
        description="Internal storage for prompt history",
        default=""
    )
    
    @property
    def prompt_history_list(self):
        """Get prompt history as list"""
        if not self.prompt_history_internal:
            return []
        return [p.strip() for p in self.prompt_history_internal.split('|||') if p.strip()]
    
    def add_to_history(self, prompt):
        """Add prompt to history"""
        current = self.prompt_history_list
        current.append(prompt)
        # Keep only last 10
        if len(current) > 10:
            current = current[-10:]
        self.prompt_history_internal = '|||'.join(current)
    
    def clear_history(self):
        """Clear all history"""
        self.prompt_history_internal = ""
    
    def reset_workflow(self):
        """Reset workflow to initial state"""
        self.has_generated = False
        self.clear_history()
        self.status_message = "Ready to generate new material"


# Workaround untuk store string list - TIDAK DIPAKAI LAGI
class PromptHistoryItem(bpy.types.PropertyGroup):
    text: bpy.props.StringProperty(name="Prompt")


# Registrasi classes
classes = (
    PromptHistoryItem,
    AIMaterialProperties,
    MATERIAL_PT_ai_generator,
    MATERIAL_PT_ai_settings,
    MATERIAL_PT_ai_examples,
)


def register():
    for cls in classes:
        bpy.utils.register_class(cls)
    
    # Register property group
    bpy.types.Scene.ai_material_props = bpy.props.PointerProperty(type=AIMaterialProperties)


def unregister():
    # Unregister property group
    del bpy.types.Scene.ai_material_props
    
    for cls in reversed(classes):
        bpy.utils.unregister_class(cls)
