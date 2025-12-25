"""
Blender Shader Node Reference
Complete list of node types and their socket names
"""

# Comprehensive node type reference with socket info and usage
NODE_TYPES = {
    # Output Nodes
    "ShaderNodeOutputMaterial": {
        "inputs": ["Surface", "Volume", "Displacement", "Thickness"],
        "outputs": [],
        "description": "Final material output node - always required",
        "common_connections": {
            "Surface": "From Principled BSDF or other shader outputs"
        }
    },
    
    # Shader Nodes
    "ShaderNodeBsdfPrincipled": {
        "inputs": ["Base Color", "Subsurface", "Subsurface Radius", "Subsurface Color", 
                   "Metallic", "Specular", "Specular Tint", "Roughness", "Anisotropic",
                   "Anisotropic Rotation", "Sheen", "Sheen Tint", "Clearcoat", 
                   "Clearcoat Roughness", "IOR", "Transmission", "Transmission Roughness",
                   "Emission", "Emission Strength", "Alpha", "Normal", "Clearcoat Normal",
                   "Tangent"],
        "outputs": ["BSDF"],
        "description": "Main shader node - handles most material properties",
        "common_connections": {
            "Base Color": "From ColorRamp.Color or texture nodes",
            "Normal": "From Bump.Normal or Normal Map.Normal",
            "BSDF": "To Material Output.Surface"
        }
    },
    "ShaderNodeBsdfDiffuse": {
        "inputs": ["Color", "Roughness", "Normal"],
        "outputs": ["BSDF"],
        "description": "Simple diffuse shader"
    },
    "ShaderNodeBsdfGlossy": {
        "inputs": ["Color", "Roughness", "Normal"],
        "outputs": ["BSDF"],
        "description": "Glossy/reflective shader"
    },
    "ShaderNodeMixShader": {
        "inputs": ["Fac", "Shader", "Shader"],
        "outputs": ["Shader"],
        "description": "Mix two shaders together based on factor",
        "common_connections": {
            "Fac": "From Fresnel.Fac or Layer Weight or texture",
            "Shader": "From any BSDF nodes",
            "Shader": "To Output Material.Surface or another Mix Shader"
        },
        "critical_inputs": {
            "Fac": {
                "requirement": "connect_or_set",
                "severity": "warning",
                "reason": "Controls shader mixing ratio"
            }
        }
    },
    "ShaderNodeAddShader": {
        "inputs": ["Shader", "Shader"],
        "outputs": ["Shader"],
        "description": "Add two shaders together (combines light contributions)",
        "common_connections": {
            "Shader": "From Emission + Diffuse/Glossy for glowing materials",
            "Shader": "To Output Material.Surface or Mix Shader"
        }
    },
    "ShaderNodeEmission": {
        "inputs": ["Color", "Strength"],
        "outputs": ["Emission"],
        "description": "Emission shader for glowing materials",
        "common_connections": {
            "Color": "From ColorRamp or RGB node",
            "Emission": "To Add Shader (combine with other shader) or Mix Shader"
        }
    },
    "ShaderNodeBsdfTransparent": {
        "inputs": ["Color"],
        "outputs": ["BSDF"],
        "description": "Transparent shader for invisible/transparent materials"
    },
    "ShaderNodeBsdfTranslucent": {
        "inputs": ["Color", "Normal"],
        "outputs": ["BSDF"],
        "description": "Translucent shader for materials like paper, wax, skin"
    },
    "ShaderNodeBsdfGlass": {
        "inputs": ["Color", "Roughness", "IOR", "Normal"],
        "outputs": ["BSDF"],
        "description": "Glass shader with refraction and reflection (combines both)",
        "common_connections": {
            "Color": "From ColorRamp or RGB node for tinted glass",
            "IOR": "1.45 (glass), 1.333 (water), 1.5 (crystal)",
            "Normal": "From Bump for surface detail (water ripples, scratches)",
            "BSDF": "To MixShader (blend with other shaders) or Output.Surface"
        },
        "usage_examples": {
            "water": "IOR=1.333, Color=blue-tint, use Bump for ripples",
            "glass": "IOR=1.45, Roughness=0.0 for clear glass",
            "frosted_glass": "IOR=1.45, Roughness=0.3-0.7"
        }
    },
    "ShaderNodeBsdfRefraction": {
        "inputs": ["Color", "Roughness", "IOR", "Normal"],
        "outputs": ["BSDF"],
        "description": "Refraction shader for transparent materials (refraction only, no reflection)",
        "common_connections": {
            "Color": "From ColorRamp for color tint",
            "IOR": "1.333 (water), 1.45 (glass) - determines bending of light",
            "BSDF": "To MixShader to blend with Glass BSDF"
        },
        "critical_note": "Often mixed with Glass BSDF for realistic water/liquid materials"
    },
    "ShaderNodeSubsurfaceScattering": {
        "inputs": ["Color", "Scale", "Radius", "IOR", "Anisotropy", "Normal"],
        "outputs": ["BSSRDF"],
        "description": "Subsurface scattering for organic materials (skin, wax, marble)"
    },
    "ShaderNodeBsdfAnisotropic": {
        "inputs": ["Color", "Roughness", "Anisotropy", "Rotation", "Normal", "Tangent"],
        "outputs": ["BSDF"],
        "description": "Anisotropic shader for brushed metal effects"
    },
    "ShaderNodeBsdfToon": {
        "inputs": ["Color", "Size", "Smooth", "Normal"],
        "outputs": ["BSDF"],
        "description": "Toon shader for cel-shading/cartoon effects"
    },
    "ShaderNodeBsdfVelvet": {
        "inputs": ["Color", "Sigma", "Normal"],
        "outputs": ["BSDF"],
        "description": "Velvet shader for fabric materials"
    },
    "ShaderNodeBsdfSheen": {
        "inputs": ["Color", "Roughness", "Normal"],
        "outputs": ["BSDF"],
        "description": "Sheen shader for fabric sheen effects"
    },
    "ShaderNodeBsdfHair": {
        "inputs": ["Color", "Offset", "RoughnessU", "RoughnessV", "Tangent"],
        "outputs": ["BSDF"],
        "description": "Hair shader for realistic hair rendering"
    },
    "ShaderNodeBackground": {
        "inputs": ["Color", "Strength"],
        "outputs": ["Background"],
        "description": "Background shader for world environment"
    },
    "ShaderNodeHoldout": {
        "inputs": [],
        "outputs": ["Holdout"],
        "description": "Holdout shader for compositing masks"
    },
    
    # Volume Shader Nodes
    "ShaderNodeVolumePrincipled": {
        "inputs": ["Color", "Density", "Anisotropy", "Absorption Color", "Emission Strength", "Emission Color", "Blackbody Intensity", "Blackbody Tint", "Temperature", "Temperature Attribute"],
        "outputs": ["Volume"],
        "description": "Principled Volume shader for volumetric effects (fog, smoke, water)",
        "common_connections": {
            "Color": "From ColorRamp or RGB for volume tint",
            "Density": "Controls volume thickness (0.0=transparent, higher=denser)",
            "Volume": "To Material Output.Volume (NOT Surface!)"
        },
        "usage_examples": {
            "water_volume": "Density=0.01, Color=blue-green tint for underwater effect",
            "fog": "Density=0.1-0.5, Color=white/gray",
            "smoke": "Density=1.0-5.0, Blackbody Intensity for heat glow"
        },
        "critical_note": "⚠️ Volume output goes to Output.Volume, NOT Output.Surface!"
    },
    "ShaderNodeVolumeAbsorption": {
        "inputs": ["Color", "Density"],
        "outputs": ["Volume"],
        "description": "Volume Absorption shader - absorbs light passing through volume",
        "common_connections": {
            "Color": "Color of absorbed light (opposite of visible color)",
            "Density": "Amount of absorption",
            "Volume": "To Material Output.Volume or Add Shader"
        }
    },
    "ShaderNodeVolumeScatter": {
        "inputs": ["Color", "Density", "Anisotropy"],
        "outputs": ["Volume"],
        "description": "Volume Scatter shader - scatters light in volume",
        "common_connections": {
            "Color": "Color of scattered light",
            "Density": "Amount of scattering",
            "Anisotropy": "-1.0 (backscatter) to 1.0 (forward scatter)",
            "Volume": "To Material Output.Volume or Add Shader"
        }
    },
    
    # Texture Nodes
    "ShaderNodeTexNoise": {
        "inputs": ["Vector", "W", "Scale", "Detail", "Roughness", "Distortion"],
        "outputs": ["Fac", "Color"],
        "description": "Procedural noise texture",
        "critical_inputs": {
            "Scale": {
                "requirement": "should_set",
                "severity": "info",
                "reason": "Controls pattern size - default 5.0 too generic"
            },
            "Detail": {
                "requirement": "should_set",
                "severity": "info",
                "reason": "Adds realism - default 2.0 lacks detail"
            }
        },
        "properties": {
            "noise_dimensions": {
                "type": "enum",
                "values": ["1D", "2D", "3D", "4D"],
                "default": "3D",
                "description": "Noise dimensionality - 3D (standard), 4D (with W input for animation/variation)"
            }
        },
        "common_connections": {
            "Vector": "From Mapping.Vector or Texture Coordinate",
            "W": "4D dimension input (only when noise_dimensions=4D) - for animation variation",
            "Fac": "To ColorRamp.Fac or Bump.Height",
            "Color": "To ColorRamp.Fac (as grayscale)"
        },
        "critical_note": """
⚠️ CRITICAL - `noise_dimensions` Property:
- **3D** (default): Standard 3D noise for most procedural textures
- **4D**: Adds W input for animation/variation without changing spatial position
  WHY: Animate W value to get different noise patterns - perfect for clouds, fire, etc.
- **2D**: Flat noise (rarely used)
- **1D**: Linear noise (very rare)

❌ NO 'Vector' output! Noise Texture ONLY outputs 'Fac' and 'Color'!
❌ NO 'Height' output! Use 'Fac' for height maps!

✅ CORRECT outputs: ONLY ' Fac' and 'Color'
✅ CORRECT usage: NoiseTexture.Fac → ColorRamp.Fac
✅ CORRECT usage: NoiseTexture.Fac → Bump.Height
✅ For 4D: {"noise_dimensions": "4D", "inputs": {"W": 0.0, "Scale": 5.0}}

INGAT: Noise Texture menerima Vector sebagai INPUT, menghasilkan Fac/Color sebagai OUTPUT!
"""
    },
    "ShaderNodeTexVoronoi": {
        "inputs": ["Vector", "W", "Scale", "Smoothness", "Exponent", "Randomness"],
        "outputs": ["Distance", "Color", "Position", "W", "Radius"],
        "description": "Voronoi/cellular texture pattern",
        "critical_inputs": {
            "Scale": {
                "requirement": "should_set",
                "severity": "info",
                "reason": "Controls cell pattern size"
            }
        },
        "common_connections": {
            "Distance": "To ColorRamp.Fac",
            "Color": "To ColorRamp.Fac or Mix nodes"
        }
    },
    "ShaderNodeTexMusgrave": {
        "inputs": ["Vector", "W", "Scale", "Detail", "Dimension", "Lacunarity", "Offset", "Gain"],
        "outputs": ["Fac"],
        "description": "Fractal/organic texture pattern",
        "critical_inputs": {
            "Scale": {
                "requirement": "should_set",
                "severity": "info",
                "reason": "Controls fractal pattern size"
            },
            "Detail": {
                "requirement": "should_set",
                "severity": "info",
                "reason": "Controls fractal complexity"
            }
        },
        "common_connections": {
            "Fac": "To ColorRamp.Fac or Bump.Height"
        }
    },
    "ShaderNodeTexWave": {
        "inputs": ["Vector", "Scale", "Distortion", "Detail", "Detail Scale", "Detail Roughness", "Phase Offset"],
        "outputs": ["Color", "Fac"],
        "description": "Wave/band pattern texture",
        "critical_inputs": {
            "Scale": {
                "requirement": "should_set",
                "severity": "info",
                "reason": "Controls wave pattern size"
            }
        },
        "common_connections": {
            "Fac": "To ColorRamp.Fac",
            "Color": "To ColorRamp.Fac"
        }
    },
    "ShaderNodeTexGradient": {
        "inputs": ["Vector"],
        "outputs": ["Color", "Fac"],
        "description": "Gradient texture"
    },
    "ShaderNodeTexMagic": {
        "inputs": ["Vector", "Scale", "Distortion"],
        "outputs": ["Color", "Fac"],
        "description": "Psychedelic pattern texture"
    },
    "ShaderNodeTexChecker": {
        "inputs": ["Vector", "Color1", "Color2", "Scale"],
        "outputs": ["Color", "Fac"],
        "description": "Checkerboard pattern"
    },
    "ShaderNodeTexBrick": {
        "inputs": ["Vector", "Color1", "Color2", "Mortar", "Scale", "Mortar Size", "Mortar Smooth", "Bias", "Brick Width", "Row Height"],
        "outputs": ["Color", "Fac"],
        "description": "Brick/masonry pattern texture for walls and architectural materials",
        "common_connections": {
            "Vector": "FROM Texture Coordinate.UV or Mapping.Vector",
            "Color": "TO ColorRamp.Fac (for base color) OR Displacement.Height (for geometry)",
            "Fac": "TO ColorRamp.Fac or Bump.Height (for mask/variation)"
        },
        "critical_note": """
⚠️ CRITICAL - Brick Texture Socket Rules:
❌ NO 'Vector' OUTPUT! Brick Texture ONLY outputs 'Color' and 'Fac'!
❌ NO 'BW' output! Use 'Fac' for grayscale/mask!

✅ CORRECT outputs: ONLY 'Color' and 'Fac'
✅ CORRECT usage for brick wall:
  - BrickTexture.Color → ColorRamp.Fac (for brick/mortar color)
  - BrickTexture.Color → Displacement.Height (for geometric depth)
  - BrickTexture.Fac → Bump.Height (optional, for pattern-based bump)

⚠️ IMPORTANT: Use UV coordinates (TexCoord.UV) for Brick Texture!
WHY: UV provides precise, non-distorted brick pattern
Object coordinates may cause stretching/distortion on non-uniform objects
        """,
        "usage_examples": {
            "brick_wall": "TexCoord.UV → BrickTexture, BrickTexture.Color → ColorRamp (brick+mortar colors)",
            "procedural_masonry": "BrickTexture.Color → both ColorRamp AND Displacement for realistic depth",
            "architectural_detail": "Scale=5.0, Mortar Size=0.02 for standard brick wall"
        }
    },
    "ShaderNodeTexImage": {
        "inputs": ["Vector"],
        "outputs": ["Color", "Alpha"],
        "description": "Image texture from file"
    },
    "ShaderNodeTexEnvironment": {
        "inputs": ["Vector"],
        "outputs": ["Color"],
        "description": "Environment texture (HDRI)"
    },
    "ShaderNodeTexSky": {
        "inputs": ["Vector"],
        "outputs": ["Color"],
        "description": "Procedural sky texture"
    },
    "ShaderNodeTexIES": {
        "inputs": ["Vector", "Strength"],
        "outputs": ["Fac"],
        "description": "IES light texture"
    },
    "ShaderNodeTexWhiteNoise": {
        "inputs": ["Vector", "W"],
        "outputs": ["Value", "Color"],
        "description": "White noise texture"
    },
    "ShaderNodeTexCoord": {
        "inputs": ["From Dupli"],
        "outputs": ["Generated", "Normal", "UV", "Object", "Camera", "Window", "Reflection"],
        "description": "Texture coordinates for positioning textures",
        "common_connections": {
            "Generated": "To Mapping.Vector (most common)",
            "UV": "To Mapping.Vector or directly to textures",
            "Object": "To Mapping.Vector"
        }
    },
    
    # Color Nodes
    "ShaderNodeValToRGB": {
        "inputs": ["Fac"],
        "outputs": ["Color", "Alpha"],
        "description": "ColorRamp - maps grayscale to color gradient",
        "critical_inputs": {
            "Fac": {
                "requirement": "must_connect",
                "severity": "error",
                "reason": "ColorRamp has NO default input - must connect from texture"
            }
        },
        "properties": {
            "color_mode": {
                "type": "enum",
                "values": ["RGB", "HSV", "HSL"],
                "default": "RGB",
                "description": "Color space for interpolation - RGB (can desaturate), HSV (vibrant), HSL (natural)"
            },
            "interpolation": {
                "type": "enum",
                "values": ["CONSTANT", "LINEAR", "EASE", "CARDINAL", "B_SPLINE"],
                "default": "LINEAR",
                "description": "Transition curve - CONSTANT (hard), LINEAR (default), EASE/CARDINAL/B_SPLINE (smooth)"
            }
        },
        "common_connections": {
            "Fac": "FROM texture.Fac or texture.Color (grayscale)",
            "Color": "TO Principled.Base Color or Mix nodes"
        },
        "critical_note": """
⚠️ CRITICAL - Properties for Realistic Materials:
- `color_mode`: RGB vs HSV/HSL affects gradient appearance dramatically
  - RGB: Can desaturate in middle (Red→Green passes through brown)
  - HSV/HSL: Vibrant transitions (Red→Green passes through yellow/orange)
- `interpolation`: Controls transition smoothness
  - CONSTANT: Sharp edges (cell-shading, distinct regions)
  - LINEAR: Default, even blend
  - EASE/CARDINAL: Smooth transitions
  - B_SPLINE: Ultra-smooth (may not reach full stop colors)

❌ NO 'Fac' OUTPUT! ColorRamp ONLY outputs 'Color' and 'Alpha'!
✅ CORRECT input: ONLY 'Fac' (receives 0-1 grayscale value)
✅ CORRECT outputs: ONLY 'Color' and 'Alpha'

INGAT: ColorRamp mengubah Fac INPUT menjadi Color OUTPUT, bukan Fac ke Fac!
"""
    },
    "ShaderNodeMix": {
        "inputs": ["Factor", "A", "B"],
        "outputs": ["Result"],
        "description": "New Mix node (Blender 3.4+) - unified for colors, values, vectors",
        "critical_inputs": {
            "Factor": {
                "requirement": "connect_or_set",
                "severity": "warning",
                "reason": "Controls mixing ratio - default 0.5 too generic"
            }
        },
        "properties": {
            "data_type": {
                "type": "enum",
                "values": ["FLOAT", "VECTOR", "RGBA"],
                "default": "FLOAT",
                "description": "Type of data to mix - CRITICAL for correct mixing behavior!"
            },
            "blend_type": {
                "type": "enum",
                "values": ["MIX", "DARKEN", "MULTIPLY", "BURN", "LIGHTEN", "SCREEN", 
                          "DODGE", "ADD", "OVERLAY", "SOFT_LIGHT", "LINEAR_LIGHT", 
                          "DIFFERENCE", "EXCLUSION", "SUBTRACT", "DIVIDE", 
                          "HUE", "SATURATION", "COLOR", "VALUE"],
                "default": "MIX",
                "description": "Blend mode (only when data_type is RGBA)",
                "applies_to": "RGBA data_type only"
            }
        },
        "common_connections": {
            "Factor": "From texture.Fac or ColorRamp.Color (as grayscale)",
            "A": "First value/color/vector to mix",
            "B": "Second value/color/vector to mix",
            "Result": "To Principled inputs or other nodes"
        },
        "critical_note": """
⚠️ CRITICAL - `data_type` Property:
- **FLOAT**: Mix single values (metallic, roughness, scale, etc.)
  Input A/B: single numbers (0.5, 0.8, etc.)
  Example: Mix two roughness values based on mask
  
- **VECTOR**: Mix 3D coordinates or normals  
  Input A/B: [X, Y, Z] arrays
  Example: Mix two UV coordinates, blend two normal maps
  
- **RGBA**: Mix colors (blend_type applies) - USE 'RGBA' NOT 'COLOR'!
  Input A/B: [R, G, B, A] arrays
  Example: Mix two base colors with specific blend mode
  
- **ROTATION**: Mix rotation values
  Input A/B: rotation values
  
⚠️ NOT the same as MixRGB! Uses Factor/A/B, NOT Fac/Color1/Color2.
⚠️ MUST set `data_type` property correctly or mixing will fail!
⚠️ Blender API uses 'RGBA' for color data type, NOT 'COLOR'!

Socket Names (important!):
- Input sockets: 'Factor', 'A', 'B' (NOT 'Fac', 'Color1', 'Color2')
- Output socket: 'Result' (NOT 'Color')

Default: FLOAT (if not specified, will mix as float values)
""",
        "usage_examples": {
            "mix_roughness": """
{
  "type": "ShaderNodeMix",
  "data_type": "FLOAT",
  "inputs": {"Factor": 0.5, "A": 0.2, "B": 0.8}
}
""",
            "mix_colors": """
{
  "type": "ShaderNodeMix",
  "data_type": "RGBA",
  "blend_type": "MULTIPLY",
  "inputs": {
    "Factor": 0.5,
    "A": [1.0, 0.5, 0.0, 1.0],
    "B": [0.0, 0.5, 1.0, 1.0]
  }
}
"""
        }
    },
    "ShaderNodeMixRGB": {
        "inputs": ["Fac", "Color1", "Color2"],
        "outputs": ["Color"],
        "description": "Legacy Mix node for colors",
        "critical_inputs": {
            "Fac": {
                "requirement": "connect_or_set",
                "severity": "warning",
                "reason": "Controls mixing ratio - default 0.5 too generic"
            }
        },
        "common_connections": {
            "Color1": "From texture or ColorRamp",
            "Color2": "From texture or ColorRamp",
            "Color": "To Principled.Base Color"
        },
        "critical_note": "❌ NO 'Normal' input! Only Fac, Color1, Color2"
    },
    "ShaderNodeHueSaturation": {
        "inputs": ["Hue", "Saturation", "Value", "Fac", "Color"],
        "outputs": ["Color"],
        "description": "Adjust hue/saturation/value"
    },
    "ShaderNodeBrightContrast": {
        "inputs": ["Color", "Bright", "Contrast"],
        "outputs": ["Color"],
        "description": "Adjust brightness/contrast"
    },
    "ShaderNodeGamma": {
        "inputs": ["Color", "Gamma"],
        "outputs": ["Color"],
        "description": "Gamma correction"
    },
    "ShaderNodeInvert": {
        "inputs": ["Fac", "Color"],
        "outputs": ["Color"],
        "description": "Invert colors"
    },
    
    # Vector Nodes
    "ShaderNodeMapping": {
        "inputs": ["Vector", "Location", "Rotation", "Scale"],
        "outputs": ["Vector"],
        "description": "Transform texture coordinates",
        "common_connections": {
            "Vector": "FROM Texture Coordinate (Generated/UV/Object)",
            "Vector": "TO texture nodes (Noise, Wave, etc)"
        },
        "critical_note": "❌ Output is 'Vector', NOT 'Generated'!"
    },
    "ShaderNodeBump": {
        "inputs": ["Strength", "Distance", "Height", "Normal"],
        "outputs": ["Normal"],
        "description": "Convert height map to normal for bump mapping",
        "critical_inputs": {
            "Height": {
                "requirement": "must_connect",
                "severity": "error",
                "reason": "Bump has NO default height - must connect from texture"
            },
            "Strength": {
                "requirement": "should_set",
                "severity": "info",
                "reason": "Controls bump intensity - explicit value gives control"
            }
        },
        "common_connections": {
            "Height": "FROM texture.Fac",
            "Normal": "TO Principled.Normal or another Bump"
        },
        "critical_note": "❌ NO Color inputs (Color1/Color2)! ❌ NO Color output! Only Normal!"
    },
    "ShaderNodeNormalMap": {
        "inputs": ["Strength", "Color"],
        "outputs": ["Normal"],
        "description": "Normal map node"
    },
    "ShaderNodeDisplacement": {
        "inputs": ["Height", "Midlevel", "Scale", "Normal"],
        "outputs": ["Displacement"],
        "description": "Displacement mapping - creates actual geometric detail",
        "critical_inputs": {
            "Height": {
                "requirement": "must_connect",
                "severity": "error",
                "reason": "Displacement has NO default height - must connect from texture"
            },
            "Scale": {
                "requirement": "should_set",
                "severity": "info",
                "reason": "Controls displacement strength"
            }
        },
        "common_connections": {
            "Height": "From ColorRamp.Color or texture.Fac",
            "Displacement": "To Material Output.Displacement (NOT Surface!)"
        },
        "critical_note": """
⚠️ CRITICAL - Displacement vs Bump:
- Displacement: Creates REAL geometric changes (needs subdivision)
- Bump: Creates ILLUSION of detail (no geometry change, faster)

Input sockets:
- Height: Value 0-1 controlling displacement amount (from ColorRamp or texture)
- Midlevel: 0.5 default (neutral height, no displacement)
- Scale: Displacement strength (0.1-0.3 typical untuk subtle, 0.5+ untuk dramatic)
- Normal: Optional normal input (can be left disconnected)

✅ CORRECT usage:
  ColorRamp.Color → Displacement.Height
  Displacement.Displacement → Output.Displacement

❌ WRONG usage:
  Displacement.Displacement → Principled.Normal (salah! ini bukan Normal!)
  Bump.Normal → Output.Displacement (salah! Normal bukan Displacement!)
  Displacement.Displacement → Output.Surface (salah! harus ke Displacement slot!)

RENDER REQUIREMENT: Mesh needs subdivision for displacement to be visible!
"""
    },
    "ShaderNodeVectorMath": {
        "inputs": ["Vector", "Vector", "Vector", "Scale"],
        "outputs": ["Vector", "Value"],
        "description": "Math operations on vectors"
    },
    "ShaderNodeVectorRotate": {
        "inputs": ["Vector", "Center", "Axis", "Angle", "Rotation"],
        "outputs": ["Vector"],
        "description": "Rotate vector"
    },
    "ShaderNodeVectorTransform": {
        "inputs": ["Vector"],
        "outputs": ["Vector"],
        "description": "Transform vector between coordinate spaces"
    },
    "ShaderNodeVectorCurve": {
        "inputs": ["Fac", "Vector"],
        "outputs": ["Vector"],
        "description": "Vector curves"
    },
    
    # Converter Nodes
    "ShaderNodeMath": {
        "inputs": ["Value", "Value", "Value"],
        "outputs": ["Value"],
        "description": "Math operations on values (ADD, SUBTRACT, MULTIPLY, DIVIDE, POWER, etc.)",
        "common_connections": {
            "Value": "FROM texture.Fac, ColorRamp.Color, or constants",
            "Value": "TO ColorRamp.Fac, Bump.Height, Mix nodes, or other Math nodes"
        },
        "critical_note": "❌ Output is 'Value', NOT 'Result'! (MapRange has 'Result', but Math only has 'Value')"
    },
    "ShaderNodeMapRange": {
        "inputs": ["Value", "From Min", "From Max", "To Min", "To Max"],
        "outputs": ["Value", "Result"],
        "description": "Remap value range"
    },
    "ShaderNodeClamp": {
        "inputs": ["Value", "Min", "Max"],
        "outputs": ["Result"],
        "description": "Clamp value to min/max"
    },
    "ShaderNodeSeparateRGB": {
        "inputs": ["Image"],
        "outputs": ["R", "G", "B"],
        "description": "Split color to channels"
    },
    "ShaderNodeCombineRGB": {
        "inputs": ["R", "G", "B"],
        "outputs": ["Image"],
        "description": "Combine channels to color"
    },
    "ShaderNodeCombineColor": {
        "inputs": ["Red", "Green", "Blue"],
        "outputs": ["Color"],
        "description": "Combine color channels (newer version)"
    },
    "ShaderNodeSeparateColor": {
        "inputs": ["Color"],
        "outputs": ["Red", "Green", "Blue"],
        "description": "Separate color to channels (newer version)"
    },
    "ShaderNodeShaderToRGB": {
        "inputs": ["Shader"],
        "outputs": ["Color", "Alpha"],
        "description": "Convert shader to RGB (for NPR effects)",
        "common_connections": {
            "Shader": "From any BSDF output",
            "Color": "To Mix or output for special effects"
        },
        "critical_note": "⚠️ Rarely used - for non-photorealistic rendering only. Most materials don't need this."
    },
    "ShaderNodeBlackbody": {
        "inputs": ["Temperature"],
        "outputs": ["Color"],
        "description": "Blackbody temperature to color"
    },
    "ShaderNodeWavelength": {
        "inputs": ["Wavelength"],
        "outputs": ["Color"],
        "description": "Wavelength to RGB color"
    },
    "ShaderNodeRGBCurve": {
        "inputs": ["Fac", "Color"],
        "outputs": ["Color"],
        "description": "RGB curves for color grading"
    },
    "ShaderNodeSeparateXYZ": {
        "inputs": ["Vector"],
        "outputs": ["X", "Y", "Z"],
        "description": "Split vector to components"
    },
    "ShaderNodeCombineXYZ": {
        "inputs": ["X", "Y", "Z"],
        "outputs": ["Vector"],
        "description": "Combine components to vector"
    },
    
    # Input Nodes
    "ShaderNodeValue": {
        "inputs": [],
        "outputs": ["Value"],
        "description": "Constant value input"
    },
    "ShaderNodeRGB": {
        "inputs": [],
        "outputs": ["Color"],
        "description": "Constant color input"
    },
    "ShaderNodeFresnel": {
        "inputs": ["IOR", "Normal"],
        "outputs": ["Fac"],
        "description": "Fresnel effect"
    },
    "ShaderNodeLayerWeight": {
        "inputs": ["Blend", "Normal"],
        "outputs": ["Fresnel", "Facing"],
        "description": "Layer weight for mixing shaders based on viewing angle",
        "common_connections": {
            "Fresnel": "To Mix Shader.Fac for angle-based mixing",
            "Facing": "To Mix Shader.Fac for edge effects"
        }
    },
    "ShaderNodeAmbientOcclusion": {
        "inputs": ["Color", "Distance", "Normal"],
        "outputs": ["Color", "AO"],
        "description": "Ambient occlusion shader input"
    },
    "ShaderNodeAttribute": {
        "inputs": [],
        "outputs": ["Color", "Vector", "Fac", "Alpha"],
        "description": "Get attribute from geometry"
    },
    "ShaderNodeBevel": {
        "inputs": ["Radius", "Normal"],
        "outputs": ["Normal"],
        "description": "Bevel shader for rounded edges"
    },
    "ShaderNodeCameraData": {
        "inputs": [],
        "outputs": ["View Vector", "View Z Depth", "View Distance"],
        "description": "Camera data information"
    },
    "ShaderNodeGeometry": {
        "inputs": [],
        "outputs": ["Position", "Normal", "Tangent", "True Normal", "Incoming", "Parametric", "Backfacing", "Pointiness", "Random Per Island"],
        "description": "Geometry data (position, normal, etc)"
    },
    "ShaderNodeLightPath": {
        "inputs": [],
        "outputs": ["Is Camera Ray", "Is Shadow Ray", "Is Diffuse Ray", "Is Glossy Ray", "Is Singular Ray", "Is Reflection Ray", "Is Transmission Ray", "Ray Length", "Ray Depth", "Diffuse Depth", "Glossy Depth", "Transparent Depth", "Transmission Depth"],
        "description": "Light path information for advanced effects"
    },
    "ShaderNodeObjectInfo": {
        "inputs": [],
        "outputs": ["Location", "Color", "Object Index", "Material Index", "Random"],
        "description": "Object information"
    },
    "ShaderNodeTangent": {
        "inputs": [],
        "outputs": ["Tangent"],
        "description": "Tangent vector for anisotropic shading"
    },
    "ShaderNodeUVMap": {
        "inputs": [],
        "outputs": ["UV"],
        "description": "UV map input"
    },
    "ShaderNodeWireframe": {
        "inputs": ["Size"],
        "outputs": ["Fac"],
        "description": "Wireframe shader"
    },
}


# Common socket name aliases untuk flexible matching
SOCKET_ALIASES = {
    # Output aliases
    "bsdf": "BSDF",
    "shader": "Shader",
    "emission": "Emission",
    "fac": "Fac",
    "factor": "Fac",
    "value": "Value",
    "color": "Color",
    "result": "Result",
    "normal": "Normal",
    "vector": "Vector",
    "alpha": "Alpha",
    
    # Input aliases
    "surface": "Surface",
    "volume": "Volume",
    "displacement": "Displacement",
    "base_color": "Base Color",
    "basecolor": "Base Color",
    "metallic": "Metallic",
    "roughness": "Roughness",
    "specular": "Specular",
    "ior": "IOR",
    "transmission": "Transmission",
    "emission": "Emission",
    "strength": "Strength",
    "height": "Height",
    "distance": "Distance",
    "scale": "Scale",
    "detail": "Detail",
    "distortion": "Distortion",
}


def get_node_info(node_type):
    """Get socket information for a node type"""
    return NODE_TYPES.get(node_type, {"inputs": [], "outputs": []})


def validate_socket(node_type, socket_name, socket_type="input"):
    """Validate if socket exists for node type"""
    node_info = get_node_info(node_type)
    sockets = node_info.get("inputs" if socket_type == "input" else "outputs", [])
    return socket_name in sockets
