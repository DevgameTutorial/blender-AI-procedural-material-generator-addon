"""
Blender AI Procedural Material Generator
Material Schema - Pydantic models untuk Gemini Structured Output
"""

from pydantic import BaseModel, Field
from typing import List, Optional, Dict, Any


class ShaderNode(BaseModel):
    """Blender shader node configuration"""
    type: str = Field(
        description="Exact Blender node type, e.g., 'ShaderNodeBsdfPrincipled', 'ShaderNodeTexWave'"
    )
    location: Optional[List[int]] = Field(
        default=[0, 0],
        min_length=2,
        max_length=2,
        description="Node position in shader editor [x, y] (optional, will be auto-arranged if not provided)"
    )
    inputs: Optional[Dict[str, Any]] = Field(
        default={},
        description="Input socket values, e.g., {'Base Color': [r,g,b,a], 'Scale': 10.0}"
    )
    
    # Node-specific properties (optional)
    blend_type: Optional[str] = Field(
        default=None,
        description="For MixRGB node: MIX, MULTIPLY, ADD, etc."
    )
    wave_type: Optional[str] = Field(
        default=None,
        description="For Wave Texture: BANDS or RINGS"
    )
    bands_direction: Optional[str] = Field(
        default=None,
        description="For Wave Texture BANDS: X, Y, Z, DIAGONAL"
    )
    rings_direction: Optional[str] = Field(
        default=None,
        description="For Wave Texture RINGS: X, Y, Z, SPHERICAL"
    )
    musgrave_type: Optional[str] = Field(
        default=None,
        description="For Musgrave: FBM, MULTIFRACTAL, RIDGED_MULTIFRACTAL, etc."
    )
    operation: Optional[str] = Field(
        default=None,
        description="For Math/VectorMath: ADD, MULTIPLY, POWER, etc."
    )
    color_ramp: Optional[Dict[str, Any]] = Field(
        default=None,
        description="For ColorRamp: {'stops': [{'position': 0.0, 'color': [r,g,b,a]}, ...]}"
    )
    
    # Mix node properties (Blender 3.4+)
    data_type: Optional[str] = Field(
        default=None,
        description="For Mix node (ShaderNodeMix): FLOAT, VECTOR, RGBA. Use RGBA for color mixing (NOT 'COLOR')!"
    )
    
    # ColorRamp properties for better control
    color_mode: Optional[str] = Field(
        default=None,
        description="For ColorRamp (ValToRGB): RGB, HSV, HSL - color space for interpolation"
    )
    interpolation: Optional[str] = Field(
        default=None,
        description="For ColorRamp (ValToRGB): CONSTANT, LINEAR, EASE, CARDINAL, B_SPLINE"
    )
    
    # Noise Texture properties
    noise_dimensions: Optional[str] = Field(
        default=None,
        description="For Noise Texture: 1D, 2D, 3D, 4D (4D enables W input for animation/variation)"
    )
    
    ior: Optional[float] = Field(
        default=None,
        description="For Glass/Refraction BSDF: Index of Refraction (1.333=water, 1.45=glass, 1.5=crystal)"
    )
    volume_density: Optional[float] = Field(
        default=None,
        description="For Volume shaders: Density of volume (0.0=transparent, higher=denser)"
    )



class NodeLink(BaseModel):
    """Connection between two shader nodes"""
    from_node: int = Field(
        ge=0,
        description="Source node index in nodes array (0-indexed)"
    )
    from_socket: str = Field(
        description="Output socket name, e.g., 'BSDF', 'Color', 'Fac', 'Normal'"
    )
    to_node: int = Field(
        ge=0,
        description="Target node index in nodes array (0-indexed)"
    )
    to_socket: str = Field(
        description="Input socket name, e.g., 'Surface', 'Base Color', 'Height'"
    )


class MaterialConfig(BaseModel):
    """Complete procedural material configuration"""
    material_name: str = Field(
        description="Descriptive material name, e.g., 'Detailed Oak Wood with Scratches', 'Brushed Aluminum with Wear Patterns'"
    )
    nodes: List[ShaderNode] = Field(
        min_length=3,
        max_length=20,
        description="""Shader nodes (3-20 nodes): CREATE FOCUSED MATERIALS WITH APPROPRIATE COMPLEXITY
        
        ADAPTIVE COMPLEXITY - Match node count to user request:
        - SIMPLE (3-8 nodes): Basic materials, color mixing, single properties
          Example: "red blue mix" → 5-7 nodes (RGB + RGB + Mix + Principled + Output)
        
        - MEDIUM (8-15 nodes): Some details, 1-2 specific features
          Example: "rusty metal with scratches" → 10-12 nodes
        
        - DETAILED (15-20 nodes): Multiple specific features with texture layers
          Example: "detailed wood with color variation and bump" → 16-20 nodes
        
        CRITICAL: Keep it FOCUSED! Quality over quantity - fewer well-connected nodes better than many disconnected nodes."""
    )
    links: List[NodeLink] = Field(
        min_length=2,
        max_length=40,
        description="""Node connections (2-40 links): Create focused node networks
        
        Minimum 2 links (for simplest materials) - Maximum 40 links (max ~2 links per node average)
        Typically: links = nodes - 1 to nodes * 1.5 (depending on complexity)
        
        IMPORTANT: Every node must be connected (no dead nodes!)"""
    )


def get_material_schema():
    """
    Get JSON schema untuk Gemini API
    
    Returns:
        dict: JSON schema compatible dengan Gemini structured output
    """
    return MaterialConfig.model_json_schema()


def validate_material_config(config_dict: dict) -> MaterialConfig:
    """
    Validate dan parse material config dari dict
    
    Args:
        config_dict: Dictionary dari AI response
        
    Returns:
        MaterialConfig: Validated Pydantic model
        
    Raises:
        ValidationError: Jika config tidak valid
    """
    return MaterialConfig.model_validate(config_dict)


def material_config_to_dict(material: MaterialConfig) -> dict:
    """
    Convert MaterialConfig ke dict untuk material_generator.py
    
    Args:
        material: Validated MaterialConfig
        
    Returns:
        dict: Dictionary compatible dengan existing material_generator
    """
    return material.model_dump()
