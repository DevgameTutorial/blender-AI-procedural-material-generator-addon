import bpy
from bpy.types import Panel, PropertyGroup
from bpy.props import StringProperty, BoolProperty, EnumProperty, PointerProperty

# =============================================================================
# CALLBACKS & UTILITIES
# =============================================================================

def on_model_change(self, context):
    """Callback saat model diubah: Otomatis menghubungkan ulang API"""
    props = context.scene.ai_material_props
    
    if props.api_initialized and props.api_key:
        print(f"[AI Material] Switching model to: {props.preferred_model}")
        
        try:
            # Mengasumsikan ai_connector ada di dalam package yang sama
            from . import ai_connector
            success = ai_connector.init_api(props.api_key, props.preferred_model)
            
            if success:
                current_model = ai_connector.get_current_model_name()
                props.current_model = current_model if current_model else props.preferred_model
                props.status_message = f"Model switched to {props.current_model}"
            else:
                props.status_message = "Failed to switch model"
        except ImportError:
            props.status_message = "Connector module not found"

# =============================================================================
# DATA PROPERTIES
# =============================================================================

class AIMaterialProperties(PropertyGroup):
    prompt: StringProperty(
        name="Prompt",
        description="Describe the material you want to create",
        default=""
    )
    
    api_key: StringProperty(
        name="API Key",
        description="Google Gemini API Key",
        default="",
        subtype='PASSWORD'
    )
    
    api_initialized: BoolProperty(name="API Initialized", default=False)
    is_generating: BoolProperty(name="Is Generating", default=False)
    has_generated: BoolProperty(name="Has Generated", default=False)
    auto_assign: BoolProperty(name="Auto Assign", default=True)
    
    status_message: StringProperty(name="Status Message", default="")
    current_model: StringProperty(name="Current Model", default="")
    
    preferred_model: EnumProperty(
        name="Model",
        items=[
            ('gemini-2.5-flash', 'Gemini 2.5 Flash (Free)', 'Recommended for speed', 'CHECKMARK', 0),
            ('gemini-2.5-pro', 'Gemini 2.5 Pro (Paid)', 'Better reasoning', 'FUND', 1),
            ('gemini-3-flash-preview', 'Gemini 3 Flash (Preview)', 'Next-gen fast model', 'FUND', 2),
            ('gemini-3-pro-preview', 'Gemini 3 Pro (Preview)', 'Most powerful model', 'FUND', 3),
        ],
        default='gemini-2.5-flash',
        update=on_model_change
    )
    
    prompt_history_internal: StringProperty(name="History Internal", default="")

    @property
    def prompt_history_list(self):
        if not self.prompt_history_internal:
            return []
        return [p.strip() for p in self.prompt_history_internal.split('|||') if p.strip()]

    def add_to_history(self, prompt):
        current = self.prompt_history_list
        if prompt not in current:
            current.append(prompt)
            if len(current) > 5: current.pop(0)
            self.prompt_history_internal = '|||'.join(current)

    def clear_history(self):
        self.prompt_history_internal = ""

# =============================================================================
# USER INTERFACE PANELS
# =============================================================================

class MATERIAL_PT_ai_base:
    """Base class untuk sharing property panel"""
    bl_space_type = 'NODE_EDITOR'
    bl_region_type = 'UI'
    bl_category = 'AI Material'
    bl_context = "shader"

class MATERIAL_PT_ai_generator(MATERIAL_PT_ai_base, Panel):
    bl_label = "AI Material Generator"
    bl_idname = "MATERIAL_PT_ai_generator"
    
    def draw(self, context):
        layout = self.layout
        props = context.scene.ai_material_props
        
        # Connection Status
        status_box = layout.box()
        if props.api_initialized:
            status_box.label(text="API Ready", icon='CHECKMARK')
        else:
            status_box.label(text="API Not Initialized", icon='ERROR')
        
        # Prompt Input
        col = layout.column(align=True)
        col.label(text="Describe Material:")
        col.prop(props, "prompt", text="")
        
        # Dynamic Buttons
        row = layout.row(align=True)
        row.scale_y = 1.5
        
        if props.is_generating:
            row.enabled = False
            row.operator("material.generate_ai", text="Generating...", icon='TIME')
        elif not props.has_generated:
            row.operator("material.generate_ai", text="Generate Material", icon='ADD')
        else:
            row.operator("material.modify_ai", text="Modify (Refine)", icon='MODIFIER')
            layout.operator("material.start_over", text="New Material", icon='FILE_REFRESH')

        # Status Message
        if props.status_message:
            layout.box().label(text=props.status_message, icon='INFO')

class MATERIAL_PT_ai_settings(MATERIAL_PT_ai_base, Panel):
    bl_label = "Settings & Model"
    bl_idname = "MATERIAL_PT_ai_settings"
    bl_parent_id = "MATERIAL_PT_ai_generator"
    bl_options = {'DEFAULT_CLOSED'}
    
    def draw(self, context):
        layout = self.layout
        props = context.scene.ai_material_props
        
        # API Key Section
        box = layout.box()
        box.label(text="Google Gemini API", icon='WORLD')
        box.prop(props, "api_key", text="")
        box.operator("material.set_api_key", text="Initialize API", icon='PLUGIN')
        
        # Model Selection
        if props.api_initialized:
            box = layout.box()
            box.label(text="Model Selection", icon='SETTINGS')
            box.prop(props, "preferred_model", text="")
            
            # Sub-info for model
            info = box.box()
            info.scale_y = 0.8
            if 'pro' in props.preferred_model or 'preview' in props.preferred_model:
                info.label(text="Requires Paid Tier / API Billing", icon='ERROR')
            else:
                info.label(text="Free Tier - Recommended", icon='CHECKMARK')

        layout.prop(props, "auto_assign", text="Auto-assign to Selected")

class MATERIAL_PT_ai_history(MATERIAL_PT_ai_base, Panel):
    bl_label = "History"
    bl_idname = "MATERIAL_PT_ai_history"
    bl_parent_id = "MATERIAL_PT_ai_generator"
    bl_options = {'DEFAULT_CLOSED'}
    
    def draw(self, context):
        layout = self.layout
        props = context.scene.ai_material_props
        history = props.prompt_history_list
        
        if not history:
            layout.label(text="No recent prompts", icon='INFO')
            return
            
        for h in reversed(history):
            layout.label(text=h[:35] + "..." if len(h) > 35 else h, icon='TIME')
        
        layout.separator()
        layout.operator("material.clear_history", text="Clear History", icon='TRASH')

# =============================================================================
# REGISTRATION
# =============================================================================

classes = (
    AIMaterialProperties,
    MATERIAL_PT_ai_generator,
    MATERIAL_PT_ai_settings,
    MATERIAL_PT_ai_history,
)

def register():
    for cls in classes:
        bpy.utils.register_class(cls)
    bpy.types.Scene.ai_material_props = PointerProperty(type=AIMaterialProperties)

def unregister():
    del bpy.types.Scene.ai_material_props
    for cls in reversed(classes):
        bpy.utils.unregister_class(cls)

if __name__ == "__main__":
    register()
