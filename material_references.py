"""
Blender AI Procedural Material Generator
Material Reference Library - Knowledge base dari berbagai tutorial material
"""

from typing import Dict, List, Tuple, Optional, Set


# ============================================================================
# MATERIAL REFERENCE DATABASE
# ============================================================================

MATERIAL_REFERENCES = {
    
    # ========================================================================
    # CARDBOARD / PAPER MATERIALS
    # ========================================================================
    
    "cardboard_damaged": {
        "name": "Damaged Cardboard Box",
        "source": "https://youtu.be/SZxsniKKG-g",
        "author": "Ryan King Art",
        "description": "Procedural cardboard dengan surface damage, creases, dan dirt/stains",
        "difficulty": "medium",
        "estimated_nodes": "12-16",
        "tags": ["cardboard", "paper", "box", "damaged", "matte", "packaging", "corrugated"],
        
        "key_techniques": [
            "Multiple noise textures at different scales for layered detail",
            "ColorRamp dengan HSL mode untuk brown tones natural, CONSTANT interpolation untuk sharp creases",
            "Bump mapping untuk surface creases dan tears",
            "Mix nodes untuk blend clean dan dirty areas",
            "Matte finish dengan high roughness",
            "3D noise untuk consistent texture tanpa stretching"
        ],
        
        "key_nodes": [
            "ShaderNodeTexCoord",
            "ShaderNodeMapping",
            "ShaderNodeTexNoise (x3 - different scales)",
            "ShaderNodeValToRGB (x3)",
            "ShaderNodeMixRGB (x2)",
            "ShaderNodeBump",
            "ShaderNodeBsdfPrincipled",
            "ShaderNodeOutputMaterial"
        ],
        
        "connection_pattern": """
=== BASE COLOR CREATION ===

[Large Scale Color Variation - Overall Tone]
TexCoord.Object → Mapping → NoiseTexture1 (Scale: 5.0, Detail: 2.0, noise_dimensions: "3D")
                             → ColorRamp1 (brown cardboard tones)
                                color_mode: "HSL"  # HSL untuk brown tones yang lebih natural
                                interpolation: "EASE"  # Smooth transitions
                             → MixRGB1.Color1

[Small Scale Detail - Dirt and Stains]
Same Mapping → NoiseTexture2 (Scale: 50.0, Detail: 10.0, Distortion: 0.2, noise_dimensions: "3D")
            → ColorRamp2 (dark spots/stains mapping)
               color_mode: "RGB"  # RGB untuk dirt yang realistic
               interpolation: "LINEAR"  # Standard blend
            → MixRGB1.Color2

[Blend Clean and Dirty]
NoiseTexture3 (Scale: 15.0, noise_dimensions: "3D") → ColorRamp3 (as mask)
                                                        color_mode: "RGB"
                                                        interpolation: "LINEAR"
                                                     → MixRGB1.Fac
MixRGB1.Color → Principled.Base Color


=== SURFACE DETAIL (Bumps and Creases) ===

[Damage Pattern]
Same Mapping → NoiseTexture4 (Scale: 20.0, Detail: 8.0, noise_dimensions: "3D")
            → ColorRamp4 (sharp contrast for creases)
               color_mode: "RGB"
               interpolation: "CONSTANT"  # CONSTANT untuk sharp creases!
            → Bump.Height

Bump.Normal → Principled.Normal


=== MATERIAL PROPERTIES ===

Principled BSDF:
  - Base Color: from MixRGB1
  - Roughness: 0.85 (very matte, no shine)
  - Specular: 0.2 (low reflectivity)
  - Metallic: 0.0
  - Normal: from Bump

Principled.BSDF → Output.Surface
        """,
        
        "color_palette": {
            "cardboard_light": [0.55, 0.45, 0.35, 1.0],
            "cardboard_medium": [0.45, 0.35, 0.25, 1.0],
            "cardboard_dark": [0.35, 0.25, 0.18, 1.0],
            "dirt_light": [0.3, 0.22, 0.15, 1.0],
            "dirt_dark": [0.2, 0.15, 0.1, 1.0],
            "damage": [0.25, 0.18, 0.12, 1.0]
        },
        
        "parameters": {
            "roughness": 0.85,
            "specular": 0.2,
            "metallic": 0.0,
            "bump_strength": 0.4,
            "bump_distance": 0.1,
            
            # Noise scales
            "noise_scale_large": 5.0,       # Overall color variation
            "noise_scale_medium": 20.0,     # Damage/creases
            "noise_scale_small": 50.0,      # Fine dirt detail
            "noise_scale_mask": 15.0,       # Blend mask
            
            # Noise detail
            "noise_detail": 8.0,
            "noise_roughness": 0.6,
            "noise_distortion": 0.2
        },
        
        "variations": {
            "clean_cardboard": {
                "description": "Less damaged, cleaner appearance",
                "changes": {
                    "bump_strength": 0.2,
                    "dirt_mix_factor": 0.3,
                    "roughness": 0.8
                }
            },
            "heavily_damaged": {
                "description": "More tears, creases, and stains",
                "changes": {
                    "bump_strength": 0.6,
                    "dirt_mix_factor": 0.7,
                    "noise_distortion": 0.4
                }
            },
            "wet_cardboard": {
                "description": "Wet/damp cardboard",
                "changes": {
                    "roughness": 0.5,
                    "specular": 0.4,
                    "colors_darker": True
                }
            }
        },
        
        "tips": [
            "Use Object coordinates to prevent stretching when editing mesh",
            "Adjust bump strength based on viewing distance (lower for far views)",
            "ColorRamp positions critical for realistic cardboard transition",
            "Multiple noise scales create depth and realism"
        ]
    },
    
    
    # ========================================================================
    # WATER / LIQUID MATERIALS
    # ========================================================================
    
    "water_realistic": {
        "name": "Realistic Water with Ripples",
        "source": "https://youtu.be/HQNOHjfDwOw",
        "author": "Polygon Runway (assumed)",
        "description": "Procedural water dengan surface ripples, refraction, dan volumetric scattering",
        "difficulty": "hard",
        "estimated_nodes": "10-12",
        "tags": ["water", "liquid", "transparent", "refraction", "volume", "ocean", "realistic"],
        
        "key_techniques": [
            "Glass BSDF + Refraction BSDF mixing untuk realistic transparency",
            "Noise texture untuk surface ripples via Bump",
            "ColorRamp dengan HSV mode untuk depth-based color variation yang vibrant",
            "Principled Volume untuk underwater light scattering",
            "IOR 1.333 untuk water physics accuracy",
            "Low roughness untuk reflective surface",
            "3D noise untuk natural water texture"
        ],
        
        "key_nodes": [
            "ShaderNodeTexCoord",
            "ShaderNodeMapping",
            "ShaderNodeTexNoise",
            "ShaderNodeValToRGB",
            "ShaderNodeBump",
            "ShaderNodeBsdfGlass",
            "ShaderNodeBsdfRefraction",
            "ShaderNodeMixShader",
            "ShaderNodeVolumePrincipled",
            "ShaderNodeOutputMaterial"
        ],
        
        "connection_pattern": """
⚠️ CRITICAL NODE FLOW - FOLLOW EXACTLY AS SPECIFIED!
==================================================================================

Rumus Node Shader untuk Material Air Realistic:

colorramp.color -> glassBSDF.color
                -> glassBSDF.bsdf -> mixshader.shader1
mixshader.shader -> materialoutput.surface

noisetexture.fac -> bump.height
bump.normal -> glassBSDF.normal

refractionBSDF.bsdf -> mixshader.shader2

principledvolume.volume -> materialoutput.volume

==================================================================================

=== PENJELASAN DETAIL ALUR NODE ===


📍 STEP 1: TEXTURE COORDINATES
-------------------------------
TexCoord.Object → Mapping.Vector
Mapping.Vector → NoiseTexture.Vector


📍 STEP 2: COLOR GENERATION (ColorRamp → Glass BSDF)
----------------------------------------------------
NoiseTexture.Fac → ColorRamp.Fac
                   color_mode: "HSV"  # HSV untuk water colors yang vibrant!
                   interpolation: "EASE"  # Smooth transitions

⚠️ CRITICAL CONNECTION:
ColorRamp.Color → GlassBSDF.Color    # ColorRamp langsung ke Glass BSDF!


📍 STEP 3: SURFACE RIPPLES (Noise → Bump → Glass Normal)
--------------------------------------------------------
NoiseTexture.Fac → Bump.Height       # Noise Fac ke Bump Height
                   Strength: 0.1
                   Distance: 0.05

Bump.Normal → GlassBSDF.Normal       # Bump Normal ke Glass BSDF Normal


📍 STEP 4: GLASS BSDF CONFIGURATION
-----------------------------------
GlassBSDF inputs:
  - Color: from ColorRamp.Color      # Dari ColorRamp
  - Normal: from Bump.Normal         # Dari Bump
  - IOR: 1.333                       # Water IOR
  - Roughness: 0.02                  # Slightly rough

⚠️ CRITICAL OUTPUT:
GlassBSDF.BSDF → MixShader.Shader (input 1)    # Glass BSDF ke Mix Shader input pertama


📍 STEP 5: REFRACTION BSDF
--------------------------
RefractionBSDF inputs:
  - IOR: 1.333                       # Water IOR
  - Roughness: 0.0                   # Smooth refraction

⚠️ CRITICAL OUTPUT:
RefractionBSDF.BSDF → MixShader.Shader (input 2)    # Refraction BSDF ke Mix Shader input kedua


📍 STEP 6: MIX SHADER → MATERIAL OUTPUT SURFACE
-----------------------------------------------
MixShader inputs:
  - Fac: 0.5                         # Balance antara Glass dan Refraction
  - Shader (input 1): from GlassBSDF.BSDF
  - Shader (input 2): from RefractionBSDF.BSDF

⚠️ CRITICAL OUTPUT:
MixShader.Shader → MaterialOutput.Surface    # Mix Shader ke Output Surface


📍 STEP 7: VOLUMETRIC SCATTERING (Optional tapi Recommended!)
-------------------------------------------------------------
PrincipledVolume inputs:
  - Color: [0.1, 0.4, 0.5, 1.0]      # Blue-green water tint
  - Density: 0.01                    # Very subtle
  - Anisotropy: 0.0

⚠️ CRITICAL OUTPUT:
PrincipledVolume.Volume → MaterialOutput.Volume    # Volume ke Output Volume (BUKAN Surface!)


==================================================================================
🎯 RINGKASAN KONEKSI UTAMA (Ikuti Rumus Ini!):
==================================================================================

1. ColorRamp.Color → GlassBSDF.Color
2. GlassBSDF.BSDF → MixShader.Shader (input 1)
3. RefractionBSDF.BSDF → MixShader.Shader (input 2)
4. MixShader.Shader → MaterialOutput.Surface
5. NoiseTexture.Fac → Bump.Height
6. Bump.Normal → GlassBSDF.Normal
7. PrincipledVolume.Volume → MaterialOutput.Volume

==================================================================================
⚠️ KESALAHAN UMUM YANG HARUS DIHINDARI:
==================================================================================

❌ JANGAN: NoiseTexture.Vector (socket tidak ada!)
✅ GUNAKAN: NoiseTexture.Fac atau NoiseTexture.Color

❌ JANGAN: Bump.Fac atau Bump.Color (output tidak ada!)
✅ GUNAKAN: Bump.Normal (output yang benar)

❌ JANGAN: PrincipledVolume.Volume → MaterialOutput.Surface
✅ GUNAKAN: PrincipledVolume.Volume → MaterialOutput.Volume

❌ JANGAN: GlassBSDF.Shader (output tidak ada!)
✅ GUNAKAN: GlassBSDF.BSDF

❌ JANGAN: ColorRamp → Mix → GlassBSDF (tidak perlu Mix di sini!)
✅ GUNAKAN: ColorRamp.Color → GlassBSDF.Color (langsung!)

==================================================================================
        """,
        
        "color_palette": {
            "water_deep": [0.05, 0.25, 0.35, 0.95],
            "water_medium": [0.1, 0.4, 0.5, 0.85],
            "water_shallow": [0.2, 0.6, 0.7, 0.7],
            "volume_tint": [0.1, 0.4, 0.5, 1.0]
        },
        
        "parameters": {
            "ior": 1.333,
            "roughness_glass": 0.02,
            "roughness_refraction": 0.0,
            "bump_strength": 0.1,
            "bump_distance": 0.05,
            "mix_factor": 0.5,
            "volume_density": 0.01,
            "noise_scale": 10.0,
            "noise_detail": 8.0,
            "noise_roughness": 0.6,
            "noise_distortion": 0.3
        },
        
        "variations": {
            "ocean_water": {
                "description": "Ocean with visible waves",
                "changes": {
                    "bump_strength": 0.4,
                    "use_wave_texture": True,
                    "roughness_glass": 0.05,
                    "volume_density": 0.02
                }
            },
            "clear_pool_water": {
                "description": "Crystal clear pool water",
                "changes": {
                    "bump_strength": 0.02,
                    "roughness_glass": 0.0,
                    "volume_density": 0.005,
                    "color_lighter": True
                }
            },
            "murky_water": {
                "description": "Dirty/swamp water",
                "changes": {
                    "color_palette": "brown-green",
                    "volume_density": 0.05,
                    "roughness_glass": 0.1
                }
            }
        },
        
        "tips": [
            "CRITICAL: IOR must be exactly 1.333 for water",
            "Volume shader goes to Output.Volume, NOT Output.Surface",
            "Keep roughness very low (0.0-0.05) for reflective water",
            "ColorRamp alpha variation creates depth perception",
            "Mix factor around 0.5 balances Glass and Refraction",
            "Bump strength depends on wave size (ocean: 0.3-0.5, pool: 0.05-0.1)"
        ]
    },
    
    
    # ========================================================================
    # METAL MATERIALS
    # ========================================================================
    
    "brushed_metal": {
        "name": "Brushed Metal/Aluminum",
        "source": "Common procedural technique",
        "author": "Industry standard pattern",
        "description": "Brushed metal dengan anisotropic reflections dan directional scratches",
        "difficulty": "medium",
        "estimated_nodes": "8-12",
        "tags": ["metal", "brushed", "aluminum", "steel", "anisotropic", "reflective", "metallic"],
        
        "key_techniques": [
            "Anisotropic shader untuk directional reflections",
            "Scaled noise texture untuk brush pattern",
            "Fresnel node untuk edge brightness",
            "Bump untuk surface micro-scratches",
            "High metallic value (1.0)"
        ],
        
        "key_nodes": [
            "ShaderNodeTexCoord",
            "ShaderNodeMapping",
            "ShaderNodeTexNoise",
            "ShaderNodeValToRGB",
            "ShaderNodeBump",
            "ShaderNodeFresnel",
            "ShaderNodeBsdfPrincipled",
            "ShaderNodeOutputMaterial"
        ],
        
        "connection_pattern": """
=== TEXTURE COORDINATES ===

TexCoord.Object → Mapping (Scale: [15, 150, 1] for brush direction)
                  → [Branch to textures]


=== BRUSH PATTERN ===

[Directional Scratches]
Mapping → NoiseTexture (Scale: 500, Detail: 15, very fine, noise_dimensions: "3D")
       → ColorRamp (aluminum color variations)
          color_mode: "HSV"  # HSV untuk metal variations yang subtle tapi vibrant
          interpolation: "EASE"  # Smooth metal transitions
       → Principled.Base Color

[Micro Surface Detail]
Same Mapping → NoiseTexture2 (Scale: 100, noise_dimensions: "3D")
            → Bump (Strength: 0.05, very subtle)
            → Principled.Normal


=== EDGE BRIGHTNESS ===

[Fresnel Effect]
Fresnel (IOR: 2.8 for aluminum) → Mix with base color (optional)


=== MATERIAL PROPERTIES ===

Principled BSDF:
  - Base Color: [0.85, 0.85, 0.88, 1.0] (light aluminum)
  - Metallic: 1.0 (full metal)
  - Roughness: 0.35 (semi-polished)
  - Specular: 0.9
  - Anisotropic: 0.7 (CRITICAL for brush effect!)
  - Anisotropic Rotation: 0.0
  - Normal: from Bump

Principled.BSDF → Output.Surface
        """,
        
        "color_palette": {
            "aluminum_light": [0.85, 0.85, 0.88, 1.0],
            "aluminum_medium": [0.75, 0.75, 0.78, 1.0],
            "aluminum_dark": [0.65, 0.65, 0.68, 1.0]
        },
        
        "parameters": {
            "metallic": 1.0,
            "roughness": 0.35,
            "specular": 0.9,
            "anisotropic": 0.7,
            "anisotropic_rotation": 0.0,
            "bump_strength": 0.05,
            "fresnel_ior": 2.8,
            "mapping_scale": [15.0, 150.0, 1.0],
            "noise_scale_fine": 500.0,
            "noise_scale_bump": 100.0,
            "noise_detail": 15.0
        },
        
        "variations": {
            "polished_metal": {
                "description": "Shiny polished metal",
                "changes": {
                    "roughness": 0.1,
                    "anisotropic": 0.0,
                    "bump_strength": 0.02
                }
            },
            "rough_metal": {
                "description": "Rough unpolished metal",
                "changes": {
                    "roughness": 0.6,
                    "bump_strength": 0.2,
                    "noise_scale_bump": 50.0
                }
            },
            "steel": {
                "description": "Steel instead of aluminum",
                "changes": {
                    "base_color": [0.7, 0.7, 0.72, 1.0],
                    "roughness": 0.3,
                    "fresnel_ior": 2.5
                }
            }
        },
        
        "tips": [
            "Anisotropic value is CRITICAL for brushed metal effect",
            "Use directional scaling in Mapping (e.g., [15, 150, 1]) for brush direction",
            "Fresnel IOR varies: Aluminum 2.8, Steel 2.5, Chrome 3.0",
            "Very high noise scale (500+) creates fine scratches",
            "Low bump strength (0.05) prevents surface from looking rough"
        ]
    },
    
    "metal_procedural": {
        "name": "Procedural Metal Material",
        "source": "https://youtu.be/q-bWV52Scus?si=3QucZmrYL8659txr",
        "author": "YouTube Tutorial",
        "description": "Material logam procedural dengan texture variation, roughness control, dan surface detail menggunakan Voronoi",
        "difficulty": "medium",
        "estimated_nodes": "10-12",
        "tags": ["metal", "procedural", "metallic", "reflective", "voronoi", "noise", "industrial"],
        
        "key_techniques": [
            "ColorRamp untuk metallic value control",
            "Noise texture untuk roughness variation",
            "Chained Mapping nodes untuk layered texture transformation",
            "Voronoi texture untuk surface pattern detail",
            "Bump mapping dari Voronoi untuk micro-surface detail"
        ],
        
        "key_nodes": [
            "ShaderNodeTexCoord",
            "ShaderNodeMapping (x2)",
            "ShaderNodeTexNoise (x2)",
            "ShaderNodeValToRGB (x2)",
            "ShaderNodeTexVoronoi",
            "ShaderNodeBump",
            "ShaderNodeBsdfPrincipled",
            "ShaderNodeOutputMaterial"
        ],
        
        "connection_pattern": """
=== TEXTURE COORDINATES ===

[Coordinate Setup]
TexCoord.Object → Mapping1.Vector

[First Mapping Branch]
Mapping1.Vector → NoiseTexture2.Vector

[Second Mapping Branch]  
TexCoord.Object → Mapping1.Vector → NoiseTexture1.Vector


=== METALLIC CONTROL ===

[Metallic Value via ColorRamp]
ColorRamp1.Color → Principled.Metallic
color_mode: "RGB"  # RGB untuk metallic value (grayscale)
interpolation: "LINEAR"  # Even metallic distribution

Note: ColorRamp1 nilai untuk control metallic strength (0.0-1.0)


=== ROUGHNESS GENERATION ===

[Noise to Roughness - IMPROVED dengan Mix node!]
Mapping1.Vector → NoiseTexture1.Vector (Scale: 5.0, Detail: 2.0, noise_dimensions: "3D")
NoiseTexture1.Fac → ColorRamp2.Fac
                     color_mode: "RGB"
                     interpolation: "EASE"  # Smooth roughness transitions
ColorRamp2.Color → Principled.Roughness

ALTERNATIF - Gunakan Mix node untuk roughness variation:
NoiseTexture1.Fac → Mix.Factor
                     data_type: "FLOAT"  # CRITICAL: Mix float values!
inputs: {"A": 0.2, "B": 0.6}  # Min/Max roughness range
Mix.Result → Principled.Roughness


=== SURFACE DETAIL (Voronoi Pattern) ===

[Layered Noise to Voronoi]
Mapping1.Vector → NoiseTexture2.Vector (Scale: 3.0, Detail: 2.0, noise_dimensions: "3D")
NoiseTexture2.Color → Mapping2.Vector
Mapping2.Vector → VoronoiTexture.Vector (Scale: 10.0)

[Voronoi to Bump]
VoronoiTexture.Color → Bump.Height
Bump.Normal → Principled.Normal


=== MATERIAL PROPERTIES ===

Principled BSDF:
  - Base Color: [0.8, 0.8, 0.82, 1.0] (metal color)
  - Metallic: from ColorRamp1
  - Roughness: from ColorRamp2 (atau Mix node)
  - Specular: 0.9
  - Normal: from Bump

Principled.BSDF → Output.Surface
        """,
        
        "color_palette": {
            "metal_base": [0.8, 0.8, 0.82, 1.0],
            "metal_dark": [0.6, 0.6, 0.62, 1.0],
            "metal_bright": [0.95, 0.95, 0.97, 1.0]
        },
        
        "parameters": {
            "metallic": 1.0,  # Via ColorRamp1
            "roughness": 0.4,  # Via ColorRamp2
            "specular": 0.9,
            "bump_strength": 0.3,
            "bump_distance": 0.1,
            
            # Noise Texture 1 (untuk Roughness)
            "noise1_scale": 5.0,
            "noise1_detail": 2.0,
            "noise1_roughness": 0.5,
            "noise1_distortion": 0.0,
            
            # Noise Texture 2 (untuk Voronoi chain)
            "noise2_scale": 3.0,
            "noise2_detail": 2.0,
            "noise2_roughness": 0.5,
            "noise2_distortion": 0.0,
            
            # Voronoi Texture
            "voronoi_scale": 10.0,
            "voronoi_randomness": 1.0,
            
            # Mapping
            "mapping1_scale": [1.0, 1.0, 1.0],
            "mapping2_scale": [1.0, 1.0, 1.0]
        },
        
        "variations": {
            "rough_metal": {
                "description": "Metal dengan surface lebih kasar",
                "changes": {
                    "roughness": 0.7,
                    "bump_strength": 0.5,
                    "voronoi_scale": 15.0
                }
            },
            "polished_metal": {
                "description": "Metal yang sangat dipoles/shiny",
                "changes": {
                    "roughness": 0.1,
                    "bump_strength": 0.1,
                    "noise1_scale": 10.0
                }
            },
            "industrial_metal": {
                "description": "Metal industrial dengan pattern kuat",
                "changes": {
                    "bump_strength": 0.6,
                    "voronoi_scale": 20.0,
                    "voronoi_randomness": 0.5
                }
            }
        },
        
        "tips": [
            "ColorRamp1 mengontrol metallic value - atur gradient untuk variasi metallic",
            "ColorRamp2 mengontrol roughness - gradient hitam-putih untuk rough variation",
            "Chained Mapping nodes memberikan kontrol transform yang lebih detail",
            "VoronoiTexture menciptakan cell pattern untuk detail surface",
            "Bump dari Voronoi memberikan micro-detail yang realistis",
            "Object coordinates mencegah stretching saat mesh diedit"
        ]
    },
    
    
    # ========================================================================
    # WOOD MATERIALS
    # ========================================================================
    
    "old_wood": {
        "name": "Old Wood/Timber with Grain",
        "source": "Common procedural technique",
        "author": "Industry standard pattern",
        "description": "Wood material dengan visible grain pattern, knots, dan natural color variation",
        "difficulty": "medium",
        "estimated_nodes": "10-14",
        "tags": ["wood", "timber", "grain", "organic", "natural", "plank", "oak", "pine"],
        
        "key_techniques": [
            "Wave texture untuk wood grain pattern",
            "Noise texture untuk knots dan imperfections",
            "ColorRamp dengan HSL mode untuk brown wood tones yang natural, B_SPLINE untuk ultra-smooth grain",
            "Bump untuk grain relief",
            "Anisotropic untuk fiber direction (optional)",
            "3D noise untuk consistent knot pattern"
        ],
        
        "key_nodes": [
            "ShaderNodeTexCoord",
            "ShaderNodeMapping",
            "ShaderNodeTexWave",
            "ShaderNodeTexNoise",
            "ShaderNodeValToRGB (x2)",
            "ShaderNodeMixRGB",
            "ShaderNodeBump",
            "ShaderNodeBsdfPrincipled",
            "ShaderNodeOutputMaterial"
        ],
        
        "connection_pattern": """
=== TEXTURE COORDINATES ===

TexCoord.Object → Mapping (Rotation: [0, 0, 0.785] for grain angle)
                  → [Branch to textures]


=== WOOD GRAIN ===

[Primary Grain Pattern]
Mapping → WaveTexture (Scale: 4, Distortion: 2.5, Detail: 6)
          Wave Type: BANDS
          Bands Direction: Z
          wave_profile: "SAW"  # Sawtooth wave untuk realistic wood grain
       → ColorRamp1 (wood grain colors: dark → medium → light brown)
          color_mode: "HSL"  # HSL untuk wood browns yang SANGAT natural!
          interpolation: "B_SPLINE"  # Ultra-smooth wood grain transitions
       → MixRGB.Color1

[Knots and Imperfections]
Same Mapping → NoiseTexture (Scale: 30, Detail: 10, noise_dimensions: "3D")
            → ColorRamp2 (darker spots for knots)
               color_mode: "RGB"  # RGB untuk dark knots
               interpolation: "LINEAR"
            → MixRGB.Color2

MixRGB (blend grain and knots) → Principled.Base Color


=== SURFACE DETAIL ===

[Grain Relief]
WaveTexture.Fac → Bump (Strength: 0.25)
NoiseTexture.Fac → Bump (add variation)
Bump.Normal → Principled.Normal


=== MATERIAL PROPERTIES ===

Principled BSDF:
  - Base Color: from MixRGB
  - Metallic: 0.0
  - Roughness: 0.65 (natural wood)
  - Specular: 0.3
  - Anisotropic: 0.4 (wood fiber direction - optional)
  - Sheen: 0.15 (slight fabric-like sheen)
  - Clearcoat: 0.1 (optional polish/finish)
  - Normal: from Bump

Principled.BSDF → Output.Surface
        """,
        
        "color_palette": {
            "wood_dark_grain": [0.15, 0.08, 0.04, 1.0],
            "wood_medium": [0.35, 0.18, 0.08, 1.0],
            "wood_light": [0.52, 0.28, 0.14, 1.0],
            "wood_lighter": [0.62, 0.38, 0.22, 1.0],
            "wood_lightest": [0.72, 0.48, 0.3, 1.0]
        },
        
        "parameters": {
            "metallic": 0.0,
            "roughness": 0.65,
            "specular": 0.3,
            "anisotropic": 0.4,
            "sheen": 0.15,
            "clearcoat": 0.1,
            "bump_strength": 0.25,
            "wave_scale": 4.0,
            "wave_distortion": 2.5,
            "wave_detail": 6.0,
            "noise_scale": 30.0,
            "noise_detail": 10.0
        },
        
        "variations": {
            "polished_wood": {
                "description": "Polished/varnished wood",
                "changes": {
                    "roughness": 0.3,
                    "clearcoat": 0.5,
                    "bump_strength": 0.15
                }
            },
            "weathered_wood": {
                "description": "Old weathered wood",
                "changes": {
                    "roughness": 0.85,
                    "bump_strength": 0.4,
                    "colors_darker": True
                }
            },
            "dark_oak": {
                "description": "Dark oak wood",
                "changes": {
                    "color_palette": "darker browns",
                    "roughness": 0.7
                }
            }
        },
        
        "tips": [
            "Wave texture is KEY for realistic grain pattern",
            "Use rotation in Mapping to control grain direction",
            "ColorRamp with 4-5 stops creates realistic color variation",
            "Combine Wave and Noise for both grain AND imperfections",
            "Anisotropic follows wood fiber direction (optional but adds realism)"
        ]
    },
    
    "wood_simple_procedural": {
        "name": "Simple Procedural Wood",
        "source": "User-provided pattern",
        "author": "Basic wood pattern",
        "description": "Simple procedural wood material menggunakan Noise Texture untuk wood grain",
        "difficulty": "easy",
        "estimated_nodes": "6-8",
        "tags": ["wood", "procedural", "simple", "noise", "basic", "grain"],
        
        "key_techniques": [
            "Noise texture untuk wood grain pattern",
            "ColorRamp dengan HSL mode untuk wood color variation yang natural",
            "Object coordinates untuk stable texture mapping",
            "Simple pattern ideal untuk learning atau quick materials",
            "3D noise untuk consistent grain tanpa stretching"
        ],
        
        "key_nodes": [
            "ShaderNodeTexCoord",
            "ShaderNodeMapping",
            "ShaderNodeTexNoise",
            "ShaderNodeValToRGB",
            "ShaderNodeBsdfPrincipled",
            "ShaderNodeOutputMaterial"
        ],
        
        "connection_pattern": """
=== TEXTURE COORDINATES ===

TexCoord.Object → Mapping.Vector
Mapping.Vector → NoiseTexture.Vector


=== WOOD GRAIN GENERATION ===

[Noise Pattern for Wood Grain]
NoiseTexture (noise_dimensions: "3D") .Fac → ColorRamp.Fac
                                              color_mode: "HSL"  # HSL untuk wood browns yang natural!
                                              interpolation: "EASE"  # Smooth wood grain
ColorRamp.Color → Principled.Base Color

⚠️ CRITICAL SOCKET RULES - SERING SALAH!
- NoiseTexture OUTPUT: HANYA "Fac" dan "Color" (❌ TIDAK ADA "Vector" atau "Height")
- ColorRamp INPUT: HANYA "Fac" (❌ TIDAK ADA input lain)
- ColorRamp OUTPUT: HANYA "Color" dan "Alpha" (❌ TIDAK ADA output "Fac")

✅ CORRECT Connection Flow:
  NoiseTexture.Fac → ColorRamp.Fac → ColorRamp.Color → Principled.Base Color

❌ WRONG Examples (NEVER DO THIS!):
  NoiseTexture.Vector → (socket tidak ada!)
  NoiseTexture.Height → (socket tidak ada!)
  ColorRamp.Fac → Principled (ColorRamp TIDAK punya output Fac!)


=== MATERIAL PROPERTIES ===

Principled BSDF:
  - Base Color: from ColorRamp.Color
  - Metallic: 0.0
  - Roughness: 0.65 (natural wood)
  - Specular: 0.3
  - Normal: (none untuk simple version)

Principled.BSDF → Output.Surface
        """,
        
        "color_palette": {
            "wood_dark": [0.25, 0.12, 0.06, 1.0],
            "wood_medium": [0.45, 0.25, 0.12, 1.0],
            "wood_light": [0.65, 0.40, 0.20, 1.0],
            "wood_lightest": [0.80, 0.55, 0.30, 1.0]
        },
        
        "parameters": {
            "metallic": 0.0,
            "roughness": 0.65,
            "specular": 0.3,
            "bump_strength": 0.0,  # No bump for simple version
            
            # Noise Texture settings
            "noise_scale": 8.0,
            "noise_detail": 5.0,
            "noise_roughness": 0.5,
            "noise_distortion": 0.3,
            
            # Mapping
            "mapping_scale": [1.0, 1.0, 1.0],
            "mapping_rotation": [0.0, 0.0, 0.0]
        },
        
        "variations": {
            "fine_grain": {
                "description": "Fine grain wood (smaller pattern)",
                "changes": {
                    "noise_scale": 15.0,
                    "noise_detail": 8.0
                }
            },
            "coarse_grain": {
                "description": "Coarse grain wood (larger pattern)",
                "changes": {
                    "noise_scale": 4.0,
                    "noise_detail": 3.0
                }
            },
            "dark_wood": {
                "description": "Darker wood tones",
                "changes": {
                    "color_palette": "darker browns",
                    "roughness": 0.7
                }
            }
        },
        
        "tips": [
            "⚠️ CRITICAL: NoiseTexture hanya punya output 'Fac' dan 'Color', TIDAK ADA 'Vector' atau 'Height'!",
            "⚠️ CRITICAL: ColorRamp input hanya 'Fac', output hanya 'Color' dan 'Alpha', TIDAK ADA output 'Fac'!",
            "Use Object coordinates untuk prevent texture stretching saat edit mesh",
            "Adjust noise_scale untuk control grain size (higher = smaller pattern)",
            "ColorRamp dengan 3-4 stops creates realistic wood color variation",
            "Untuk grain lebih realistis, gunakan 'old_wood' pattern yang menggunakan Wave Texture"
        ],
        
        "critical_warnings": [
            "❌ NEVER: NoiseTexture.Vector → ... (output 'Vector' TIDAK ADA!)",
            "❌ NEVER: NoiseTexture.Height → ... (output 'Height' TIDAK ADA!)",
            "❌ NEVER: ColorRamp.Fac → ... (ColorRamp TIDAK punya output 'Fac'!)",
            "✅ ALWAYS: Use NoiseTexture.Fac or NoiseTexture.Color as output",
            "✅ ALWAYS: ColorRamp input is 'Fac', output is 'Color' or 'Alpha'"
        ]
    },
    
    "wood_realistic": {
        "name": "Realistic Wood with UV Mapping, Bump and Displacement",
        "source": "User-provided realistic wood pattern",
        "author": "Confirmed realistic wood technique",
        "description": "Realistic procedural wood material menggunakan UV coordinates, Noise Texture untuk wood grain, dengan bump mapping dan displacement untuk detail surface dan geometric yang realistis",
        "difficulty": "medium",
        "estimated_nodes": "11",
        "tags": ["wood", "realistic", "uv", "noise", "bump", "displacement", "detailed", "procedural"],
        
        "key_techniques": [
            "UV coordinates untuk consistent texture mapping tanpa distortion",
            "Mapping node untuk transform control (scale, rotation, location)",
            "Single Noise Texture untuk efficiency - digunakan untuk 3 different outputs",
            "Multiple ColorRamps dengan different settings untuk base color, bump, dan displacement",
            "Bump mapping untuk surface relief (illusionary detail)",
            "Displacement mapping untuk actual geometric changes (real detail)",
            "3D noise dimensions untuk coherent wood grain pattern"
        ],
        
        "key_nodes": [
            "ShaderNodeTexCoord",
            "ShaderNodeMapping",
            "ShaderNodeTexNoise",
            "ShaderNodeValToRGB (x3)",  # ColorRamp1 (base color), ColorRamp2 (bump), ColorRamp3 (displacement)
            "ShaderNodeBump",
            "ShaderNodeDisplacement",
            "ShaderNodeBsdfPrincipled",
            "ShaderNodeOutputMaterial"
        ],
        
        "connection_pattern": """
=== TEXTURE COORDINATES (UV-Based) ===

[UV Mapping Setup - CRITICAL for realistic wood!]
TexCoord.UV → Mapping.Vector
Mapping.Vector → NoiseTexture.Vector

⚠️ WHY UV instead of Object/Generated?
- UV provides precise, non-distorted texture mapping
- Consistent grain direction across entire object
- Better control over texture scale and placement
- Recommended for realistic materials


=== BASE COLOR GENERATION (Wood Grain Color) ===

[Wood Grain Color from Noise]
NoiseTexture (noise_dimensions: "3D") .Fac → ColorRamp1.Fac
                                              color_mode: "HSL"  # HSL untuk natural wood browns yang warm!
                                              interpolation: "B_SPLINE"  # Ultra-smooth grain transitions
ColorRamp1.Color → Principled.Base Color

⚠️ ColorRamp1 Settings untuk Realistic Wood:
- Stop 1 (pos 0.0): Dark brown [0.25, 0.12, 0.06, 1.0] (dark grain lines)
- Stop 2 (pos 0.4): Medium brown [0.45, 0.25, 0.12, 1.0]
- Stop 3 (pos 0.7): Light brown [0.65, 0.40, 0.20, 1.0]
- Stop 4 (pos 1.0): Lightest [0.80, 0.55, 0.30, 1.0] (light wood areas)


=== BUMP MAPPING (Surface Relief Detail) ===

[Same Noise source for coherent bump]
NoiseTexture.Fac → ColorRamp2.Fac
                    color_mode: "RGB"  # RGB untuk height values (grayscale)
                    interpolation: "EASE"  # Smooth surface transitions
ColorRamp2.Color → Bump.Height
Bump.Normal → Principled.Normal

⚠️ CRITICAL: Bump creates SURFACE DETAIL ILLUSION
- Does NOT change actual geometry
- Fast to render
- Bump.Normal connects to Principled.Normal
- Bump strength range: 0.1-0.4 (subtle to pronounced)


=== DISPLACEMENT MAPPING (Real Geometric Detail) ===

[Same Noise source for displacement coherence]
NoiseTexture.Fac → ColorRamp3.Fac
                    color_mode: "RGB"  # RGB untuk displacement values
                    interpolation: "LINEAR"  # Controlled displacement strength
ColorRamp3.Color → Displacement.Height
Displacement.Displacement → Output.Displacement

⚠️ CRITICAL: Displacement creates ACTUAL GEOMETRIC CHANGES
- Requires mesh subdivision to be visible
- Displacement.Displacement connects to Output.Displacement (NOT Surface!)
- Scale range: 0.05-0.2 (subtle to strong geometric detail)

Displacement node inputs:
  - Height: from ColorRamp3.Color (0-1 grayscale controlling displacement amount)
  - Midlevel: 0.5 (neutral height - no displacement)
  - Scale: 0.1-0.15 (displacement strength - adjust based on mesh size)
  - Normal: (optional - can be left disconnected)


=== MATERIAL PROPERTIES ===

Principled BSDF:
  - Base Color: from ColorRamp1.Color (wood grain colors)
  - Metallic: 0.0 (wood is non-metallic)
  - Roughness: 0.6-0.7 (natural wood - matte to semi-matte)
  - Specular: 0.3 (low reflectivity)
  - Normal: from Bump.Normal (surface detail)

Material Output:
  - Surface: from Principled.BSDF
  - Displacement: from Displacement.Displacement (geometric detail)


=== COMPLETE CONNECTION FLOW (Step by Step) ===

1. TexCoord.UV → Mapping.Vector
2. Mapping.Vector → NoiseTexture.Vector
3. NoiseTexture.Fac → ColorRamp1.Fac
4. ColorRamp1.Color → Principled.Base Color
5. Principled.BSDF → Output.Surface
6. NoiseTexture.Fac → ColorRamp2.Fac
7. ColorRamp2.Color → Bump.Height
8. Bump.Normal → Principled.Normal
9. NoiseTexture.Fac → ColorRamp3.Fac
10. ColorRamp3.Color → Displacement.Height
11. Displacement.Displacement → Output.Displacement


⚠️ CRITICAL SOCKET RULES - NEVER FORGET!
- NoiseTexture OUTPUT: ONLY "Fac" and "Color" (NO "Vector", NO "Height")
- ColorRamp INPUT: ONLY "Fac"
- ColorRamp OUTPUT: ONLY "Color" and "Alpha" (NO "Fac" output!)
- Bump OUTPUT: ONLY "Normal" → goes to Principled.Normal
- Displacement OUTPUT: ONLY "Displacement" → goes to Output.Displacement
- Principled OUTPUT: "BSDF" → goes to Output.Surface
        """,
        
        "color_palette": {
            "wood_dark_grain": [0.25, 0.12, 0.06, 1.0],   # Dark grain lines
            "wood_medium": [0.45, 0.25, 0.12, 1.0],       # Medium brown
            "wood_light": [0.65, 0.40, 0.20, 1.0],        # Light brown
            "wood_lightest": [0.80, 0.55, 0.30, 1.0]      # Lightest highlights
        },
        
        "parameters": {
            "metallic": 0.0,
            "roughness": 0.65,
            "specular": 0.3,
            
            # Noise Texture settings (SHARED untuk color, bump, dan displacement - EFFICIENT!)
            "noise_scale": 8.0,      # Controls wood grain frequency
            "noise_detail": 5.0,     # Adds fine detail to grain
            "noise_roughness": 0.5,  # Controls noise contrast
            "noise_distortion": 0.3, # Adds variation to grain pattern
            "noise_dimensions": "3D", # CRITICAL: 3D for coherent pattern
            
            # Bump settings
            "bump_strength": 0.2,    # Surface relief strength (0.1-0.4 range)
            "bump_distance": 0.1,    # Distance for normal calculation
            
            # Displacement settings
            "displacement_scale": 0.1,     # Geometric detail strength (0.05-0.2 range)
            "displacement_midlevel": 0.5,  # Neutral height (0.5 = no displacement)
            
            # Mapping settings
            "mapping_location": [0.0, 0.0, 0.0],
            "mapping_rotation": [0.0, 0.0, 0.0],
            "mapping_scale": [1.0, 1.0, 1.0]  # Adjust untuk control grain size
        },
        
        "variations": {
            "fine_grain_wood": {
                "description": "Fine detailed wood grain (smaller pattern)",
                "changes": {
                    "noise_scale": 12.0,
                    "noise_detail": 8.0,
                    "bump_strength": 0.15,
                    "displacement_scale": 0.08
                }
            },
            "coarse_grain_wood": {
                "description": "Coarse wood grain (larger, more visible pattern)",
                "changes": {
                    "noise_scale": 5.0,
                    "noise_detail": 3.0,
                    "bump_strength": 0.3,
                    "displacement_scale": 0.15
                }
            },
            "polished_wood": {
                "description": "Polished/varnished wood surface",
                "changes": {
                    "roughness": 0.3,
                    "bump_strength": 0.1,
                    "displacement_scale": 0.05,
                    "specular": 0.5
                }
            },
            "weathered_wood": {
                "description": "Old weathered wood dengan heavy surface detail",
                "changes": {
                    "roughness": 0.8,
                    "bump_strength": 0.4,
                    "displacement_scale": 0.2,
                    "noise_distortion": 0.5,
                    "colors_darker": True
                }
            },
            "dark_oak": {
                "description": "Dark oak wood dengan rich brown tones",
                "changes": {
                    "color_palette": {
                        "wood_dark_grain": [0.15, 0.08, 0.04, 1.0],
                        "wood_medium": [0.30, 0.18, 0.08, 1.0],
                        "wood_light": [0.45, 0.28, 0.14, 1.0],
                        "wood_lightest": [0.55, 0.35, 0.20, 1.0]
                    },
                    "roughness": 0.7
                }
            }
        },
        
        "tips": [
            "⚠️ CRITICAL: Use UV coordinates untuk consistent, non-distorted wood texture!",
            "⚠️ CRITICAL: Single NoiseTexture.Fac dapat connect ke MULTIPLE ColorRamps (efficient!)",
            "⚠️ CRITICAL: Bump.Normal → Principled.Normal (surface illusion)",
            "⚠️ CRITICAL: Displacement.Displacement → Output.Displacement (real geometry)",
            "Bump creates surface detail WITHOUT changing geometry (fast)",
            "Displacement creates REAL geometric changes (needs subdivision surface modifier)",
            "Use ColorRamp1 (HSL, B_SPLINE) untuk smooth, natural wood colors",
            "Use ColorRamp2 (RGB, EASE) untuk smooth bump transitions",
            "Use ColorRamp3 (RGB, LINEAR) untuk controlled displacement",
            "Adjust Mapping.Scale untuk control overall grain size",
            "Noise Scale 5-12 range works well untuk realistic wood grain",
            "Bump Strength 0.1-0.4 untuk subtle to pronounced surface detail",
            "Displacement Scale 0.05-0.2 untuk realistic geometric variation",
            "RENDER REQUIREMENT: Add Subdivision Surface modifier untuk visible displacement!"
        ],
        
        "critical_warnings": [
            "❌ NEVER: NoiseTexture.Vector → ... (NoiseTexture has NO 'Vector' OUTPUT!)",
            "❌ NEVER: NoiseTexture.Height → ... (NoiseTexture has NO 'Height' OUTPUT!)",
            "❌ NEVER: ColorRamp.Fac → ... (ColorRamp has NO 'Fac' OUTPUT!)",
            "❌ NEVER: Bump.Normal → Output.Displacement (Wrong! Bump is NOT displacement!)",
            "❌ NEVER: Displacement.Displacement → Principled (Goes to Output.Displacement!)",
            "✅ ALWAYS: NoiseTexture outputs are 'Fac' or 'Color' ONLY",
            "✅ ALWAYS: ColorRamp input is 'Fac', outputs are 'Color' or 'Alpha'",
            "✅ ALWAYS: Bump.Normal → Principled.Normal",
            "✅ ALWAYS: Displacement.Displacement → Output.Displacement",
            "✅ ALWAYS: Use UV coordinates untuk realistic material mapping"
        ]
    },
    
    "wood_advanced_procedural": {
        "name": "Advanced Procedural Wood with Bump and Displacement (Object Coordinates)",
        "source": "User-provided advanced pattern (Object coord version)",
        "author": "Enhanced wood pattern",
        "description": "Advanced procedural wood dengan Object coordinates (alternative to UV), Noise Texture untuk grain, bump mapping untuk surface detail, dan displacement untuk geometric detail",
        "difficulty": "medium",
        "estimated_nodes": "10-12",
        "tags": ["wood", "procedural", "advanced", "noise", "bump", "displacement", "detailed", "object"],
        
        "key_techniques": [
            "Object coordinates untuk dynamic texture mapping",
            "Noise texture dengan 3D dimensions untuk wood grain pattern (base color)",
            "ColorRamp dengan HSL mode dan B_SPLINE untuk ultra-smooth natural wood",
            "Bump mapping untuk surface relief tanpa mengubah geometry",
            "Displacement mapping untuk actual geometric detail",
            "Multiple ColorRamps dari single Noise Texture untuk efficiency dan coherence",
            "Different interpolation modes untuk berbagai output (color vs height)"
        ],
        
        "key_nodes": [
            "ShaderNodeTexCoord",
            "ShaderNodeMapping",
            "ShaderNodeTexNoise",
            "ShaderNodeValToRGB (x3)",  # ColorRamp1 (color), ColorRamp2 (bump), ColorRamp3 (displacement)
            "ShaderNodeBump",
            "ShaderNodeDisplacement",
            "ShaderNodeBsdfPrincipled",
            "ShaderNodeOutputMaterial"
        ],
        
        "connection_pattern": """
=== TEXTURE COORDINATES (Object-Based) ===

TexCoord.Object → Mapping.Vector
Mapping.Vector → NoiseTexture.Vector

⚠️ Object coordinates vs UV:
- Object: Dynamic, adapts to mesh transformations
- UV: Fixed, consistent mapping (better for realistic materials)
- Use Object when UV unwrap is not available


=== BASE COLOR GENERATION ===

[Wood Grain Color]
NoiseTexture (noise_dimensions: "3D") .Fac → ColorRamp1.Fac
                                              color_mode: "HSL"  # HSL untuk natural wood browns!
                                              interpolation: "B_SPLINE"  # Ultra-smooth grain
ColorRamp1.Color → Principled.Base Color


=== BUMP MAPPING (Surface Detail) ===

[Same Noise Texture for Bump]
NoiseTexture.Fac → ColorRamp2.Fac
                    color_mode: "RGB"  # RGB untuk bump height values
                    interpolation: "EASE"  # Smooth bump transitions
ColorRamp2.Color → Bump.Height
Bump.Normal → Principled.Normal

⚠️ CRITICAL: Bump creates surface detail ILLUSION without changing geometry
⚠️ Bump.Normal connects to Principled.Normal (NOT to Output!)


=== DISPLACEMENT MAPPING (Geometric Detail) ===

[Same Noise Texture for Displacement]
NoiseTexture.Fac → ColorRamp3.Fac
                    color_mode: "RGB"  # RGB untuk displacement values
                    interpolation: "LINEAR"  # Controlled displacement
ColorRamp3.Color → Displacement.Height
Displacement.Displacement → Output.Displacement

⚠️ CRITICAL: Displacement creates ACTUAL geometric changes
⚠️ Displacement output goes to Output.Displacement (NOT Surface!)

Displacement node inputs:
  - Height: from ColorRamp3.Color
  - Midlevel: 0.5 (default - determines neutral height)
  - Scale: 0.1-0.3 (controls displacement strength)
  - Normal: (optional - can be left disconnected)


=== MATERIAL PROPERTIES ===

Principled BSDF:
  - Base Color: from ColorRamp1.Color
  - Metallic: 0.0
  - Roughness: 0.65 (natural wood)
  - Specular: 0.3
  - Normal: from Bump.Normal

Material Output:
  - Surface: from Principled.BSDF
  - Displacement: from Displacement.Displacement


⚠️ CRITICAL SOCKET RULES:
- NoiseTexture OUTPUT: HANYA "Fac" dan "Color"
- ColorRamp INPUT: HANYA "Fac"
- ColorRamp OUTPUT: HANYA "Color" dan "Alpha"
- Bump OUTPUT: HANYA "Normal" → goes to Principled.Normal
- Displacement OUTPUT: HANYA "Displacement" → goes to Output.Displacement
        """,
        
        "color_palette": {
            "wood_dark": [0.25, 0.12, 0.06, 1.0],
            "wood_medium": [0.45, 0.25, 0.12, 1.0],
            "wood_light": [0.65, 0.40, 0.20, 1.0],
            "wood_lightest": [0.80, 0.55, 0.30, 1.0]
        },
        
        "parameters": {
            "metallic": 0.0,
            "roughness": 0.65,
            "specular": 0.3,
            
            # Noise Texture settings (shared untuk color, bump, dan displacement)
            "noise_scale": 10.0,
            "noise_detail": 6.0,
            "noise_roughness": 0.5,
            "noise_distortion": 0.4,
            
            # Bump settings
            "bump_strength": 0.2,  # Subtle surface detail
            "bump_distance": 0.1,
            
            # Displacement settings
            "displacement_scale": 0.15,  # Actual geometric detail
            "displacement_midlevel": 0.5,  # Neutral height
            
            # Mapping
            "mapping_scale": [1.0, 1.0, 1.0],
            "mapping_rotation": [0.0, 0.0, 0.0]
        },
        
        "variations": {
            "subtle_detail": {
                "description": "Subtle bump and displacement untuk smooth wood",
                "changes": {
                    "bump_strength": 0.1,
                    "displacement_scale": 0.08,
                    "noise_scale": 12.0
                }
            },
            "pronounced_grain": {
                "description": "Strong grain dengan visible displacement",
                "changes": {
                    "bump_strength": 0.4,
                    "displacement_scale": 0.25,
                    "noise_scale": 8.0,
                    "noise_detail": 8.0
                }
            },
            "weathered_plank": {
                "description": "Weathered wood dengan heavy displacement",
                "changes": {
                    "bump_strength": 0.5,
                    "displacement_scale": 0.3,
                    "noise_distortion": 0.6,
                    "roughness": 0.8,
                    "colors_darker": True
                }
            }
        },
        
        "tips": [
            "⚠️ CRITICAL: 1 NoiseTexture dapat digunakan untuk multiple outputs (efficient!)",
            "⚠️ CRITICAL: NoiseTexture.Fac dapat di-connect ke multiple ColorRamps",
            "⚠️ CRITICAL: Bump.Normal → Principled.Normal (untuk surface detail)",
            "⚠️ CRITICAL: Displacement.Displacement → Output.Displacement (untuk geometry)",
            "Bump creates ILLUSION of detail (fast, no geometry change)",
            "Displacement creates REAL geometry (slower, needs subdivision)",
            "Use different ColorRamp settings untuk control bump vs displacement intensity",
            "ColorRamp2 (bump): sharper contrast untuk more visible bumps",
            "ColorRamp3 (displacement): gentler gradient untuk smoother displacement",
            "Displacement Scale 0.1-0.3 good range untuk wood (higher = more extreme)",
            "Untuk render dengan displacement, enable Subdivision di mesh modifier"
        ],
        
        "critical_warnings": [
            "❌ NEVER: NoiseTexture.Vector → ... (output 'Vector' TIDAK ADA!)",
            "❌ NEVER: NoiseTexture.Height → ... (output 'Height' TIDAK ADA!)",
            "❌ NEVER: ColorRamp.Fac → ... sebagai output (Fac adalah INPUT!)",
            "❌ NEVER: Bump.Normal → Output.Displacement (Normal bukan Displacement!)",
            "❌ NEVER: Displacement.Displacement → Principled.Normal (salah node!)",
            "✅ ALWAYS: Bump.Normal → Principled.Normal",
            "✅ ALWAYS: Displacement.Displacement → Output.Displacement",
            "✅ ALWAYS: Same NoiseTexture.Fac dapat ke multiple ColorRamps"
        ],
        
        "render_notes": [
            "Displacement memerlukan mesh dengan cukup subdivision untuk terlihat",
            "Tambahkan Subdivision Surface modifier dengan 4-6 subdivisions",
            "Gunakan Adaptive Subdivision di Cycles untuk best results",
            "Bump tidak memerlukan subdivision - works on any mesh"
        ]
    },
    
    "tree_bark": {
        "name": "Procedural Tree Bark",
        "source": "User-provided pattern",
        "author": "Tree bark pattern",
        "description": "Procedural tree bark material dengan Voronoi cell pattern, noise variation, dan displacement untuk realistic bark texture",
        "difficulty": "medium-hard",
        "estimated_nodes": "14-18",
        "tags": ["tree", "bark", "wood", "organic", "procedural", "nature", "voronoi", "displacement"],
        
        "key_techniques": [
            "Voronoi texture untuk bark cell pattern",
            "Multiple noise textures untuk color dan surface variation",
            "Chained Mapping dengan Noise untuk distortion effect",
            "ColorRamp chains untuk bark color complexity",
            "Displacement untuk actual geometric bark relief",
            "Bump combination untuk layered surface detail",
            "Math ADD node untuk combining height values"
        ],
        
        "key_nodes": [
            "ShaderNodeTexCoord",
            "ShaderNodeTexNoise (x3)",
            "ShaderNodeMixRGB (x2)",
            "ShaderNodeMapping",
            "ShaderNodeTexVoronoi",
            "ShaderNodeValToRGB (x4)",
            "ShaderNodeMath (ADD operation)",
            "ShaderNodeBump",
            "ShaderNodeDisplacement",
            "ShaderNodeBsdfPrincipled",
            "ShaderNodeOutputMaterial"
        ],
        
        "connection_pattern": """
=== TEXTURE COORDINATES ===

[Main Coordinate Source]
TexCoord.Object → NoiseTexture1.Vector
TexCoord.Object → MixRGB1.Color1


=== BASE COLOR DISTORTION ===

[Noise for Distortion]
NoiseTexture1.Color → MixRGB1.Color2
MixRGB1.Color → Mapping.Vector

⚠️ CRITICAL: NoiseTexture OUTPUT adalah 'Color' (bukan 'Vector'!)
WHY: Noise digunakan untuk distort koordinat sebelum masuk ke Voronoi


[Distorted Voronoi Pattern]
Mapping.Vector → VoronoiTexture1.Vector


=== BASE COLOR CREATION ===

[Voronoi to Color]
VoronoiTexture1.Distance → ColorRamp1.Fac
ColorRamp1.Color → MixRGB2.Color1

[Noise Variation]
NoiseTexture2.Fac → ColorRamp2.Fac
ColorRamp2.Color → MixRGB2.Color2

[Mix Factor from Noise]
NoiseTexture3.Fac → ColorRamp3.Fac
ColorRamp3.Color → MixRGB2.Fac

⚠️ CRITICAL: ColorRamp OUTPUT hanya 'Color', BUKAN 'Fac'!

MixRGB2.Color → Principled.Base Color


=== ROUGHNESS ===

[Voronoi to Roughness]
VoronoiTexture1.Distance → ColorRamp4.Fac
ColorRamp4.Color → Principled.Roughness


=== SURFACE DETAIL (Bump + Displacement) ===

[Combine Heights for Detail]
VoronoiTexture1.Distance → Math_ADD.Value (first input)
NoiseTexture3.Fac → Math_ADD.Value (second input)

⚠️ CRITICAL: Math node dengan operasi ADD menggunakan socket 'Value', BUKAN 'Result'!

Math_ADD.Value → Bump.Height
Math_ADD.Value → Displacement.Height

[Apply to Material]
Bump.Normal → Principled.Normal
Displacement.Displacement → Output.Displacement

⚠️ CRITICAL: Displacement.Displacement → Output.Displacement (BUKAN Output.Surface!)


=== FINAL OUTPUT ===

Principled.BSDF → Output.Surface
        """,
        
        "color_palette": {
            "bark_dark": [0.15, 0.10, 0.06, 1.0],
            "bark_medium": [0.28, 0.18, 0.10, 1.0],
            "bark_light": [0.42, 0.28, 0.16, 1.0],
            "bark_highlight": [0.52, 0.38, 0.22, 1.0]
        },
        
        "parameters": {
            "metallic": 0.0,
            "roughness": 0.75,  # Via ColorRamp4
            "specular": 0.2,
            "bump_strength": 0.5,
            "bump_distance": 0.1,
            "displacement_scale": 0.15,
            "displacement_midlevel": 0.5,
            
            # NoiseTexture1 (untuk distortion)
            "noise1_scale": 5.0,
            "noise1_detail": 4.0,
            "noise1_roughness": 0.5,
            "noise1_distortion": 0.0,
            
            # NoiseTexture2 (untuk color variation)
            "noise2_scale": 8.0,
            "noise2_detail": 5.0,
            "noise2_roughness": 0.5,
            "noise2_distortion": 0.2,
            
            # NoiseTexture3 (untuk mix factor dan bump)
            "noise3_scale": 12.0,
            "noise3_detail": 6.0,
            "noise3_roughness": 0.5,
            "noise3_distortion": 0.3,
            
            # Voronoi Texture
            "voronoi_scale": 15.0,
            "voronoi_randomness": 1.0,
            "voronoi_metric": "EUCLIDEAN",
            
            # Mapping
            "mapping_scale": [1.0, 1.0, 1.0],
            "mapping_rotation": [0.0, 0.0, 0.0],
            "mapping_location": [0.0, 0.0, 0.0]
        },
        
        "variations": {
            "rough_bark": {
                "description": "Bark dengan tekstur lebih kasar (old tree)",
                "changes": {
                    "bump_strength": 0.8,
                    "displacement_scale": 0.25,
                    "voronoi_scale": 20.0,
                    "noise3_detail": 8.0
                }
            },
            "smooth_bark": {
                "description": "Bark yang lebih halus (young tree)",
                "changes": {
                    "bump_strength": 0.2,
                    "displacement_scale": 0.05,
                    "voronoi_scale": 8.0,
                    "roughness": 0.6
                }
            },
            "dark_bark": {
                "description": "Dark oak atau mahogany bark",
                "changes": {
                    "color_palette": "darker browns",
                    "roughness": 0.8,
                    "specular": 0.15
                }
            },
            "weathered_bark": {
                "description": "Weathered/aged bark dengan detail tinggi",
                "changes": {
                    "bump_strength": 0.7,
                    "displacement_scale": 0.3,
                    "noise_distortion": 0.5,
                    "voronoi_randomness": 0.7
                }
            }
        },
        
        "tips": [
            "⚠️ CRITICAL: Voronoi.Distance HARUS ke ColorRamp.Fac, BUKAN langsung ke Principled",
            "⚠️ CRITICAL: Math ADD node memiliki socket 'Value', BUKAN 'Result'",
            "⚠️ CRITICAL: Displacement.Displacement ke Output.Displacement, BUKAN Output.Surface",
            "⚠️ CRITICAL: NoiseTexture OUTPUT hanya 'Fac' dan 'Color', TIDAK ADA 'Vector'",
            "⚠️ CRITICAL: ColorRamp OUTPUT hanya 'Color' dan 'Alpha', TIDAK ADA 'Fac'",
            "Object coordinates mencegah stretching saat mesh diedit",
            "Voronoi Scale menentukan ukuran cell pattern (15-25 untuk realistic bark)",
            "Displacement memerlukan subdivision pada mesh untuk terlihat",
            "Kombinasi Bump + Displacement memberikan detail maksimal",
            "ColorRamp4 mengontrol roughness variation untuk realism",
            "NoiseTexture1.Color digunakan untuk distort koordinat sebelum Voronoi"
        ],
        
        "critical_warnings": [
            "❌ NEVER: NoiseTexture.Vector → ... (output 'Vector' TIDAK ADA!)",
            "❌ NEVER: ColorRamp.Fac → ... sebagai output (Fac adalah INPUT!)",
            "❌ NEVER: Math.Result untuk ADD operation (gunakan Math.Value!)",
            "❌ NEVER: Displacement → Output.Surface (salah socket!)",
            "❌ NEVER: Bump.Normal → Output.Displacement (Normal bukan Displacement!)",
            "✅ ALWAYS: NoiseTexture outputs: 'Fac' atau 'Color'",
            "✅ ALWAYS: ColorRamp input: 'Fac', output: 'Color'",
            "✅ ALWAYS: Math ADD output: 'Value'",
            "✅ ALWAYS: Displacement.Displacement → Output.Displacement",
            "✅ ALWAYS: Bump.Normal → Principled.Normal"
        ],
        
        "render_notes": [
            "Displacement memerlukan mesh dengan subdivision untuk terlihat",
            "Recommended: Subdivision Surface modifier dengan 4-6 levels",
            "Gunakan Adaptive Subdivision di Cycles untuk best results",
            "Bump tidak memerlukan subdivision - bekerja pada mesh apapun",
            "Untuk render preview cepat, disable Displacement terlebih dahulu",
            "Scale Displacement 0.15-0.3 good range untuk bark (higher = more extreme)"
        ]
    },
    
    
    # ========================================================================
    # BRICK / STONE MATERIALS
    # ========================================================================
    
    "brick_wall_procedural": {
        "name": "Procedural Brick Wall",
        "source": "User-provided pattern",
        "author": "Basic brick wall pattern",
        "description": "Procedural brick wall material menggunakan Brick Texture untuk pattern, ColorRamp untuk warna, Bump untuk surface detail, dan Displacement untuk geometric detail",
        "difficulty": "medium",
        "estimated_nodes": "8-10",
        "tags": ["brick", "wall", "stone", "masonry", "building", "procedural", "displacement"],
        
        "key_techniques": [
            "Brick Texture untuk pola bata yang akurat dan realistic",
            "ColorRamp untuk mengatur warna bata dan mortar (semen)",
            "Noise Texture untuk variasi surface dan weathering effects",
            "Bump mapping untuk surface detail tanpa mengubah geometry",
            "Displacement mapping untuk geometric depth dan realism",
            "UV coordinates untuk texture mapping yang presisi"
        ],
        
        "key_nodes": [
            "ShaderNodeTexCoord",
            "ShaderNodeTexBrick",
            "ShaderNodeTexNoise",
            "ShaderNodeValToRGB",
            "ShaderNodeBump",
            "ShaderNodeDisplacement",
            "ShaderNodeBsdfPrincipled",
            "ShaderNodeOutputMaterial"
        ],
        
        "connection_pattern": """
=== TEXTURE COORDINATES ===

TexCoord.UV → BrickTexture.Vector
TexCoord.UV → NoiseTexture.Vector

⚠️ CRITICAL: Gunakan UV coordinates (BUKAN Object) untuk Brick Texture!
WHY: UV coordinates memberikan mapping yang presisi untuk brick pattern


=== BASE COLOR DARI BRICK PATTERN ===

[Brick Pattern to Color]
BrickTexture.Color → ColorRamp.Fac
                      color_mode: "HSL"  # HSL untuk natural brick-to-mortar transitions!
                      interpolation: "LINEAR"  # Even distribution
ColorRamp.Color → Principled.Base Color

⚠️ CRITICAL SOCKET RULES:
- BrickTexture OUTPUT: "Color" dan "Fac" (NO "Vector"!)
- ColorRamp INPUT: "Fac" (receives grayscale/color)
- ColorRamp OUTPUT: "Color" dan "Alpha" (NO "Fac" output!)

✅ CORRECT Connection:
  BrickTexture.Color → ColorRamp.Fac → ColorRamp.Color → Principled.Base Color


=== BUMP MAPPING (Surface Detail) ===

[Noise for Surface Variation]
NoiseTexture (noise_dimensions: "3D") .Fac → Bump.Height
Bump.Normal → Principled.Normal

⚠️ CRITICAL: Bump creates surface detail ILLUSION (fast, no geometry change)
⚠️ Bump.Normal connects to Principled.Normal (NOT to Output!)


=== DISPLACEMENT MAPPING (Geometric Detail) ===

[Brick Pattern for Displacement]
BrickTexture.Color → Displacement.Height
Displacement.Displacement → Output.Displacement

⚠️ CRITICAL: Displacement creates ACTUAL geometric changes
⚠️ Displacement output goes to Output.Displacement (NOT Surface!)

Displacement node inputs:
  - Height: from BrickTexture.Color
  - Midlevel: 0.5 (default - determines neutral height)
  - Scale: 0.1-0.3 (controls displacement strength)
  - Normal: (optional - can be left disconnected)


=== MATERIAL OUTPUT ===

Principled BSDF:
  - Base Color: from ColorRamp.Color
  - Metallic: 0.0
  - Roughness: 0.8 (rough brick surface)
  - Specular: 0.3
  - Normal: from Bump.Normal

Material Output:
  - Surface: from Principled.BSDF
  - Displacement: from Displacement.Displacement


⚠️ RENDER REQUIREMENTS:
- Mesh needs subdivision for displacement to be visible!
- Add Subdivision Surface modifier (4-6 levels) to object
- In Cycles, enable Adaptive Subdivision for best results
        """,
        
        "color_palette": {
            "brick_red": [0.65, 0.25, 0.15, 1.0],
            "brick_orange": [0.75, 0.35, 0.20, 1.0],
            "brick_dark": [0.45, 0.20, 0.12, 1.0],
            "mortar_light": [0.7, 0.7, 0.65, 1.0],
            "mortar_medium": [0.5, 0.5, 0.48, 1.0],
            "mortar_dark": [0.3, 0.3, 0.28, 1.0]
        },
        
        "parameters": {
            "metallic": 0.0,
            "roughness": 0.8,
            "specular": 0.3,
            
            # Brick Texture settings
            "brick_scale": 5.0,
            "brick_mortar_size": 0.02,
            "brick_mortar_smooth": 0.0,
            "brick_bias": 0.0,
            "brick_brick_width": 0.5,
            "brick_row_height": 0.25,
            
            # Noise Texture settings (untuk bump)
            "noise_scale": 15.0,
            "noise_detail": 8.0,
            "noise_roughness": 0.6,
            "noise_distortion": 0.3,
            
            # Bump settings
            "bump_strength": 0.3,  # Surface detail
            "bump_distance": 0.1,
            
            # Displacement settings
            "displacement_scale": 0.2,  # Geometric detail
            "displacement_midlevel": 0.5,  # Neutral height
        },
        
        "variations": {
            "clean_brick_wall": {
                "description": "Clean, new brick wall dengan minimal weathering",
                "changes": {
                    "bump_strength": 0.15,
                    "displacement_scale": 0.1,
                    "noise_scale": 20.0,
                    "roughness": 0.7
                }
            },
            "weathered_brick": {
                "description": "Weathered brick wall dengan heavy surface damage",
                "changes": {
                    "bump_strength": 0.5,
                    "displacement_scale": 0.3,
                    "noise_scale": 10.0,
                    "noise_distortion": 0.6,
                    "roughness": 0.9,
                    "colors_darker": True
                }
            },
            "old_brick_wall": {
                "description": "Old brick wall dengan crumbling mortar",
                "changes": {
                    "bump_strength": 0.6,
                    "displacement_scale": 0.35,
                    "brick_mortar_size": 0.04,
                    "noise_detail": 12.0,
                    "roughness": 0.95
                }
            }
        },
        
        "tips": [
            "⚠️ CRITICAL: Gunakan TexCoord.UV (BUKAN Object) untuk Brick Texture mapping",
            "⚠️ CRITICAL: BrickTexture.Color dapat digunakan untuk BOTH ColorRamp DAN Displacement",
            "⚠️ CRITICAL: Displacement memerlukan subdivision pada mesh (add Subdivision Surface modifier)",
            "⚠️ CRITICAL: Displacement.Displacement → Output.Displacement (BUKAN Surface!)",
            "Adjust brick_scale untuk control brick size (higher = smaller bricks)",
            "Adjust brick_mortar_size untuk control mortar thickness",
            "ColorRamp dengan 2-3 stops untuk realistic brick color (brick color → mortar color)",
            "Bump strength 0.2-0.5 untuk realistic surface detail",
            "Displacement scale 0.1-0.3 untuk subtle geometric depth",
            "Untuk render displacement, enable subdivision di mesh (4-6 levels minimum)"
        ],
        
        "critical_warnings": [
            "❌ NEVER: TexCoord.Object → BrickTexture (use UV for precise mapping!)",
            "❌ NEVER: BrickTexture.Vector → ... (output 'Vector' TIDAK ADA!)",
            "❌ NEVER: Displacement.Displacement → Principled.Normal (salah socket!)",
            "❌ NEVER: Bump.Normal → Output.Displacement (Normal bukan Displacement!)",
            "✅ ALWAYS: TexCoord.UV → BrickTexture.Vector",
            "✅ ALWAYS: BrickTexture.Color → ColorRamp.Fac",
            "✅ ALWAYS: BrickTexture.Color → Displacement.Height",
            "✅ ALWAYS: Displacement.Displacement → Output.Displacement",
            "✅ ALWAYS: Add Subdivision Surface modifier untuk melihat displacement"
        ],
        
        "render_notes": [
            "Displacement requires mesh subdivision to be visible",
            "Add Subdivision Surface modifier with 4-6 subdivisions minimum",
            "Use Adaptive Subdivision in Cycles for best performance",
            "Bump works on any mesh without subdivision",
            "UV unwrap object before applying material for best results"
        ]
    },
    
    
    # ========================================================================
    # FABRIC MATERIALS
    # ========================================================================
    
    "fabric_cloth": {
        "name": "Fabric/Cloth Material",
        "source": "Common procedural technique",
        "author": "Industry standard pattern",
        "description": "Soft fabric material dengan weave pattern, sheen, dan subtle fuzz",
        "difficulty": "easy",
        "estimated_nodes": "6-10",
        "tags": ["fabric", "cloth", "textile", "cotton", "soft", "matte", "sheen"],
        
        "key_techniques": [
            "Noise texture untuk weave pattern",
            "Sheen shader property untuk fabric highlight",
            "Bump untuk fabric texture",
            "Low specular untuk matte surface",
            "ColorRamp untuk fabric color variation"
        ],
        
        "key_nodes": [
            "ShaderNodeTexCoord",
            "ShaderNodeTexNoise",
            "ShaderNodeValToRGB",
            "ShaderNodeBump",
            "ShaderNodeBsdfPrincipled",
            "ShaderNodeOutputMaterial"
        ],
        
        "connection_pattern": """
=== TEXTURE COORDINATES ===

TexCoord.Object → NoiseTexture (Scale: 100, Detail: 8, fine weave)


=== FABRIC COLOR ===

[Weave Pattern]
NoiseTexture → ColorRamp (fabric color with slight variation)
            → Principled.Base Color


=== SURFACE TEXTURE ===

[Fabric Weave Bumps]
NoiseTexture.Fac → Bump (Strength: 0.1, subtle texture)
Bump.Normal → Principled.Normal


=== MATERIAL PROPERTIES ===

Principled BSDF:
  - Base Color: from ColorRamp
  - Metallic: 0.0
  - Roughness: 0.8 (matte fabric)
  - Specular: 0.2 (low reflectivity)
  - Sheen: 0.5 (CRITICAL for fabric look!)
  - Sheen Tint: 0.5 (colored sheen)
  - Normal: from Bump

Principled.BSDF → Output.Surface
        """,
        
        "color_palette": {
            "fabric_red": [0.7, 0.15, 0.15, 1.0],
            "fabric_blue": [0.2, 0.3, 0.6, 1.0],
            "fabric_green": [0.3, 0.5, 0.3, 1.0],
            "fabric_white": [0.9, 0.9, 0.9, 1.0],
            "fabric_black": [0.1, 0.1, 0.1, 1.0]
        },
        
        "parameters": {
            "metallic": 0.0,
            "roughness": 0.8,
            "specular": 0.2,
            "sheen": 0.5,
            "sheen_tint": 0.5,
            "bump_strength": 0.1,
            "noise_scale": 100.0,
            "noise_detail": 8.0
        },
        
        "variations": {
            "velvet": {
                "description": "Velvet fabric",
                "changes": {
                    "roughness": 0.9,
                    "sheen": 0.8,
                    "bump_strength": 0.15
                }
            },
            "silk": {
                "description": "Silk fabric",
                "changes": {
                    "roughness": 0.3,
                    "sheen": 0.3,
                    "specular": 0.5,
                    "bump_strength": 0.05
                }
            },
            "canvas": {
                "description": "Rough canvas",
                "changes": {
                    "roughness": 0.9,
                    "bump_strength": 0.2,
                    "noise_scale": 50.0
                }
            }
        },
        
        "tips": [
            "Sheen parameter is ESSENTIAL for fabric appearance",
            "High roughness (0.8+) for matte fabric look",
            "Fine noise scale (100+) creates weave texture",
            "Low bump strength (0.1) prevents surface looking plastic",
            "Sheen Tint adds colored highlight (like fabric microfibers)"
        ]
    },
    
    "fabric_procedural": {
        "name": "Procedural Fabric/Kain",
        "source": "User-provided pattern",
        "author": "Fabric pattern dengan wave textures",
        "description": "Material kain procedural menggunakan Wave Texture untuk fabric pattern, ColorRamp untuk color variation, dan Bump mapping untuk surface detail",
        "difficulty": "medium",
        "estimated_nodes": "14-18",
        "tags": ["fabric", "cloth", "kain", "textile", "procedural", "wave", "pattern"],
        
        "key_techniques": [
            "Dual Wave Textures untuk fabric weave pattern",
            "Multiple Noise Textures untuk surface detail dan variation",
            "ColorRamp chains untuk fabric color variation and shading",
            "Triple Bump mapping untuk layered surface detail",
            "Mix nodes untuk blending wave patterns",
            "Value node untuk unified scale control"
        ],
        
        "key_nodes": [
            "ShaderNodeTexCoord",
            "ShaderNodeValue",
            "ShaderNodeTexWave (x2)",
            "ShaderNodeTexNoise (x2)",
            "ShaderNodeValToRGB (x4)",
            "ShaderNodeMix or ShaderNodeMixRGB",
            "ShaderNodeBump (x3)",
            "ShaderNodeBsdfPrincipled",
            "ShaderNodeOutputMaterial"
        ],
        
        "connection_pattern": """
=== TEXTURE COORDINATES ===

TexCoord.UV → WaveTexture1.Vector
TexCoord.UV → WaveTexture2.Vector
TexCoord.UV → NoiseTexture1.Vector
TexCoord.UV → NoiseTexture2.Vector


=== SCALE CONTROL ===

[Unified Scale Value]
Value Node → WaveTexture1.Scale
Value Node → WaveTexture2.Scale

⚠️ CRITICAL: Menggunakan single Value node untuk control scale kedua Wave Texture
WHY: Memudahkan penyesuaian fabric pattern size secara bersamaan


=== FABRIC WEAVE PATTERN ===

[Wave Pattern 1]
WaveTexture1.Color → ColorRamp1.Fac
ColorRamp1.Color → Mix.A

[Wave Pattern 2]
WaveTexture2.Color → ColorRamp2.Fac
ColorRamp2.Color → Mix.B

[Blend Two Wave Patterns]
Mix.Result → ColorRamp3.Fac
Mix.Result → ColorRamp4.Fac

⚠️ CRITICAL SOCKET RULES:
- WaveTexture OUTPUT: "Color" dan "Fac" (NO "Vector"!)
- ColorRamp INPUT: "Fac" (receives grayscale value)
- ColorRamp OUTPUT: "Color" dan "Alpha" (NO "Fac" output!)
- Mix/MixRGB OUTPUT: "Result" atau "Color" (tergantung node type)

✅ CORRECT Connection Flow:
  WaveTexture.Color → ColorRamp.Fac → ColorRamp.Color → Mix input


=== BASE COLOR GENERATION ===

[Final Color from Mixed Patterns]
ColorRamp3.Color → Principled.Base Color

⚠️ ColorRamp3 mengontrol fabric base color (warna kain)


=== ROUGHNESS GENERATION ===

[Roughness from Mixed Patterns]
ColorRamp4.Color → Principled.Roughness

⚠️ ColorRamp4 mengontrol roughness variation (fabric texture matte/shiny areas)


=== SURFACE DETAIL (Triple Bump Mapping) ===

[Bump Layer 1 - Wave Pattern Detail]
Mix.Result → Bump1.Height
Bump1.Normal → Bump2.Normal

[Bump Layer 2 - Noise Detail 1]
NoiseTexture1.Fac → Bump2.Height
Bump2.Normal → Bump3.Normal

[Bump Layer 3 - Noise Detail 2]
NoiseTexture2.Fac → Bump3.Height
Bump3.Normal → Principled.Normal

⚠️ CRITICAL: Bump chain untuk layered surface detail
WHY: Multiple bump layers create realistic fabric texture dengan varying detail
⚠️ CRITICAL: Final bump (Bump3.Normal) connects to Principled.Normal


=== MATERIAL OUTPUT ===

Principled BSDF:
  - Base Color: from ColorRamp3.Color
  - Roughness: from ColorRamp4.Color
  - Metallic: 0.0
  - Specular: 0.3
  - Sheen: 0.5 (untuk fabric highlight effect)
  - Normal: from Bump3.Normal (chained from Bump1 → Bump2 → Bump3)

Principled.BSDF → Output.Surface


⚠️ CRITICAL KONEKSI FLOW:
Wave → ColorRamp → Mix → ColorRamp (color/roughness) → Principled
Wave/Noise → Bump chain → Principled.Normal
        """,
        
        "color_palette": {
            "fabric_white": [0.9, 0.9, 0.9, 1.0],
            "fabric_beige": [0.85, 0.75, 0.65, 1.0],
            "fabric_light_gray": [0.7, 0.7, 0.7, 1.0],
            "fabric_medium_gray": [0.5, 0.5, 0.5, 1.0],
            "fabric_dark": [0.3, 0.3, 0.3, 1.0],
            "fabric_red": [0.75, 0.2, 0.2, 1.0],
            "fabric_blue": [0.2, 0.4, 0.7, 1.0],
            "fabric_green": [0.3, 0.6, 0.3, 1.0]
        },
        
        "parameters": {
            "metallic": 0.0,
            "roughness": 0.7,
            "specular": 0.3,
            "sheen": 0.5,
            "unified_scale": 10.0,
            "wave1_scale": 10.0,
            "wave1_distortion": 1.0,
            "wave1_detail": 2.0,
            "wave1_detail_scale": 3.0,
            "wave1_wave_type": "BANDS",
            "wave2_scale": 10.0,
            "wave2_distortion": 1.0,
            "wave2_detail": 2.0,
            "wave2_detail_scale": 3.0,
            "wave2_wave_type": "BANDS",
            "noise1_scale": 15.0,
            "noise1_detail": 8.0,
            "noise1_roughness": 0.5,
            "noise1_distortion": 0.0,
            "noise2_scale": 20.0,
            "noise2_detail": 10.0,
            "noise2_roughness": 0.5,
            "noise2_distortion": 0.0,
            "mix_factor": 0.5,
            "mix_blend_type": "MIX",
            "bump1_strength": 0.2,
            "bump1_distance": 0.1,
            "bump2_strength": 0.15,
            "bump2_distance": 0.1,
            "bump3_strength": 0.1,
            "bump3_distance": 0.1
        },
        
        "variations": {
            "fine_fabric": {
                "description": "Fine weave fabric dengan subtle detail",
                "changes": {
                    "unified_scale": 15.0,
                    "bump1_strength": 0.15,
                    "bump2_strength": 0.1,
                    "bump3_strength": 0.05,
                    "roughness": 0.6
                }
            },
            "coarse_fabric": {
                "description": "Coarse weave fabric dengan pronounced texture",
                "changes": {
                    "unified_scale": 6.0,
                    "bump1_strength": 0.3,
                    "bump2_strength": 0.2,
                    "bump3_strength": 0.15,
                    "roughness": 0.8
                }
            },
            "silk_like": {
                "description": "Smooth silk-like fabric",
                "changes": {
                    "unified_scale": 20.0,
                    "bump1_strength": 0.1,
                    "bump2_strength": 0.05,
                    "bump3_strength": 0.03,
                    "roughness": 0.3,
                    "sheen": 0.7,
                    "specular": 0.5
                }
            },
            "canvas": {
                "description": "Rough canvas fabric",
                "changes": {
                    "unified_scale": 8.0,
                    "bump1_strength": 0.4,
                    "bump2_strength": 0.3,
                    "bump3_strength": 0.2,
                    "roughness": 0.9,
                    "sheen": 0.2
                }
            }
        },
        
        "tips": [
            "⚠️ CRITICAL: Use WaveTexture.Color output, NOT Vector!",
            "⚠️ CRITICAL: ColorRamp has NO Fac output, only Color and Alpha!",
            "⚠️ CRITICAL: Bump chain (Bump1 → Bump2 → Bump3) untuk layered detail",
            "⚠️ CRITICAL: Single Value node controls both Wave Texture scales untuk unified control",
            "Adjust unified_scale untuk control overall fabric pattern size",
            "Wave Texture distortion creates natural fabric irregularities",
            "Triple bump layers create realistic multi-scale fabric texture",
            "Sheen parameter (0.5) is essential untuk fabric highlight effect",
            "Mix node blends two wave patterns untuk complex weave patterns",
            "ColorRamp3 controls base color, ColorRamp4 controls roughness variation",
            "Higher noise scale creates finer surface detail",
            "Bump strength cascade (0.2 → 0.15 → 0.1) prevents over-bumping"
        ],
        
        "critical_warnings": [
            "❌ NEVER: WaveTexture.Vector → ... (Wave has NO Vector output!)",
            "❌ NEVER: WaveTexture.Height → ... (Wave has NO Height output!)",
            "❌ NEVER: ColorRamp.Fac → ... as output (Fac is INPUT only!)",
            "❌ NEVER: NoiseTexture.Vector → ... (Noise has NO Vector output!)",
            "❌ NEVER: Skip Bump chaining (must chain Bump1 → Bump2 → Bump3 → Principled)",
            "✅ ALWAYS: WaveTexture.Color → ColorRamp.Fac",
            "✅ ALWAYS: ColorRamp.Color → Mix input or Principled input",
            "✅ ALWAYS: Chain bumps: Bump1.Normal → Bump2.Normal → Bump3.Normal → Principled.Normal",
            "✅ ALWAYS: Final Bump (Bump3) Normal goes to Principled.Normal",
            "✅ ALWAYS: Use single Value node untuk unified scale control"
        ]
    }
}


# ============================================================================
# HELPER FUNCTIONS
# ============================================================================

def get_reference(material_id: str) -> Optional[Dict]:
    """
    Get specific material reference by ID
    
    Args:
        material_id: ID of the material reference
        
    Returns:
        Material reference dict atau None jika tidak ditemukan
    """
    return MATERIAL_REFERENCES.get(material_id)


def search_references(query: str = None, tags: List[str] = None, 
                     difficulty: str = None) -> List[Tuple[str, Dict]]:
    """
    Search material references by keywords, tags, or difficulty
    
    Args:
        query: Search query (searches in name, description, tags)
        tags: List of tags to filter by
        difficulty: Filter by difficulty level (easy/medium/hard)
        
    Returns:
        List of tuples (material_id, reference_dict)
    """
    results = []
    query_lower = query.lower() if query else ""
    
    for mat_id, ref in MATERIAL_REFERENCES.items():
        # Filter by difficulty
        if difficulty and ref.get("difficulty") != difficulty:
            continue
        
        # Search by query
        if query:
            search_in = (
                ref["name"].lower() + " " +
                ref["description"].lower() + " " +
                " ".join(ref["tags"]).lower()
            )
            if query_lower not in search_in:
                continue
        
        # Filter by tags
        if tags:
            ref_tags = set(ref["tags"])
            query_tags = set(tags)
            if not query_tags.intersection(ref_tags):
                continue
        
        results.append((mat_id, ref))
    
    return results


def get_all_tags() -> List[str]:
    """
    Get all unique tags from all references
    
    Returns:
        Sorted list of unique tags
    """
    all_tags = set()
    for ref in MATERIAL_REFERENCES.values():
        all_tags.update(ref["tags"])
    return sorted(all_tags)


def get_references_by_tag(tag: str) -> List[Tuple[str, Dict]]:
    """
    Get all references with a specific tag
    
    Args:
        tag: Tag to search for
        
    Returns:
        List of tuples (material_id, reference_dict)
    """
    return search_references(tags=[tag])


def get_similar_references(material_id: str, limit: int = 3) -> List[Tuple[str, Dict, int]]:
    """
    Get similar materials based on overlapping tags
    
    Args:
        material_id: ID of the reference material
        limit: Maximum number of similar references to return
        
    Returns:
        List of tuples (material_id, reference_dict, overlap_count)
        Sorted by overlap count (descending)
    """
    ref = get_reference(material_id)
    if not ref:
        return []
    
    similar = []
    ref_tags = set(ref["tags"])
    
    for mat_id, other_ref in MATERIAL_REFERENCES.items():
        if mat_id == material_id:
            continue
        
        other_tags = set(other_ref["tags"])
        overlap_count = len(ref_tags & other_tags)
        
        if overlap_count > 0:
            similar.append((mat_id, other_ref, overlap_count))
    
    # Sort by overlap count (descending)
    similar.sort(key=lambda x: x[2], reverse=True)
    return similar[:limit]


def list_all_references() -> List[Tuple[str, str, str]]:
    """
    List all available references with basic info
    
    Returns:
        List of tuples (material_id, name, difficulty)
    """
    return [
        (mat_id, ref["name"], ref["difficulty"])
        for mat_id, ref in MATERIAL_REFERENCES.items()
    ]


def get_reference_summary(material_id: str) -> str:
    """
    Get formatted summary of a material reference
    
    Args:
        material_id: ID of the material
        
    Returns:
        Formatted string summary
    """
    ref = get_reference(material_id)
    if not ref:
        return f"Reference '{material_id}' not found"
    
    summary = f"""
Material: {ref['name']}
Difficulty: {ref['difficulty']}
Nodes: {ref['estimated_nodes']}
Source: {ref['source']}
Tags: {', '.join(ref['tags'])}

Description:
{ref['description']}

Key Techniques:
{chr(10).join('  - ' + t for t in ref['key_techniques'])}
    """.strip()
    
    return summary


def convert_reference_to_example_json(material_id: str) -> Optional[Dict]:
    """
    Convert reference pattern ke contoh JSON structure yang valid
    Ini memberikan AI contoh konkret bagaimana struktur node+link seharusnya
    
    Args:
        material_id: ID of the material reference
        
    Returns:
        Dict dengan example JSON structure atau None jika tidak bisa parse
    """
    ref = get_reference(material_id)
    if not ref or 'key_nodes' not in ref:
        return None
    
    # Create minimal example structure based on key_nodes
    # Ini adalah simplified version, bukan full implementation
    example_nodes = []
    
    # Parse key_nodes untuk get node types
    node_types = []
    for node_desc in ref['key_nodes']:
        # Extract node type (e.g., "ShaderNodeTexNoise (x3)" -> "ShaderNodeTexNoise")
        node_type = node_desc.split('(')[0].strip()
        
        # Handle multiplier (x2, x3, etc)
        if '(x' in node_desc:
            try:
                count = int(node_desc.split('(x')[1].split(')')[0])
                node_types.extend([node_type] * count)
            except:
                node_types.append(node_type)
        else:
            node_types.append(node_type)
    
    # Build example nodes array
    for i, node_type in enumerate(node_types):
        example_nodes.append({
            "type": node_type,
            "location": [i * 200, 0],
            "inputs": {}
        })
    
    # Create basic structure
    example = {
        "material_name": ref['name'],
        "nodes": example_nodes[:5],  # Limit to 5 nodes for brevity
        "links": [
            # Example links will be generic
            {"from_node": 0, "from_socket": "Output", "to_node": 1, "to_socket": "Input"}
        ]
    }
    
    return example


def get_critical_socket_warnings(material_id: str) -> str:
    """
    Generate critical socket warnings untuk material tertentu
    Ini menekankan socket names yang HARUS benar
    
    Args:
        material_id: ID of the material
        
    Returns:
        Formatted warning text
    """
    ref = get_reference(material_id)
    if not ref:
        return ""
    
    warnings = []
    
    # Generic warnings untuk semua material
    warnings.append("⚠️ CRITICAL SOCKET RULES:")
    warnings.append("• TexCoord outputs: Object, UV, Generated, Normal (NO 'Vector'!)")
    warnings.append("• Mapping outputs: Vector (NO 'Object'!)")
    warnings.append("• Noise/Wave/Voronoi outputs: Fac, Color (NO 'Vector' output!)")
    warnings.append("• Bump inputs: Height, Strength | outputs: Normal (NO 'Fac'!)")
    warnings.append("• ColorRamp inputs: Fac | outputs: Color, Alpha (NO 'Fac' output!)")
    
    # Specific warnings based on material type
    tags = ref.get('tags', [])
    
    if 'water' in tags or 'liquid' in tags:
        warnings.append("\n⚠️ WATER MATERIAL SPECIFIC:")
        warnings.append("• Volume node: ShaderNodeVolumePrincipled (NO 'BsdfPrincipledVolume'!)")
        warnings.append("• Glass BSDF inputs: Color, Normal, IOR, Roughness")
        warnings.append("• Refraction BSDF inputs: Color, Normal, IOR, Roughness")
        warnings.append("• MixShader inputs: Fac, Shader, Shader (two shader inputs!)")
        warnings.append("• Volume → Output.Volume (NO Output.Surface!)")
    
    if 'metal' in tags:
        warnings.append("\n⚠️ METAL MATERIAL SPECIFIC:")
        warnings.append("• Principled BSDF: Metallic must be 1.0")
        warnings.append("• Use Anisotropic for brushed metal effect")
    
    return "\n".join(warnings)


def format_reference_for_ai(material_id: str, include_full_pattern: bool = False) -> Dict:
    """
    Format reference information for AI prompt enhancement
    Returns dict instead of string untuk better integration
    
    Args:
        material_id: ID of the material
        include_full_pattern: Include detailed connection pattern
        
    Returns:
        Dict dengan reference context untuk AI
    """
    ref = get_reference(material_id)
    if not ref:
        return {}
    
    # Build comprehensive reference context
    context = {
        "material_id": material_id,
        "name": ref['name'],
        "difficulty": ref['difficulty'],
        "estimated_nodes": ref['estimated_nodes'],
        "key_techniques": ref['key_techniques'],
        "key_nodes": ref['key_nodes'],
        "parameters": {},
        "color_palette": ref.get('color_palette', {}),
        "connection_pattern": ref.get('connection_pattern', '') if include_full_pattern else '',
        "tips": ref.get('tips', []),
        "critical_socket_warnings": get_critical_socket_warnings(material_id),
        "example_json": convert_reference_to_example_json(material_id)
    }
    
    # Extract important parameters
    params = ref['parameters']
    for key, value in params.items():
        if key in ['roughness', 'metallic', 'specular', 'ior', 'bump_strength',
                   'noise_scale', 'wave_scale', 'mix_factor', 'volume_density']:
            context['parameters'][key] = value
    
    return context


def format_reference_as_text(reference_dict: Dict) -> str:
    """
    Convert reference dict ke formatted text untuk prompt
    Helper function untuk backward compatibility
    
    Args:
        reference_dict: Dict dari format_reference_for_ai()
        
    Returns:
        Formatted text string
    """
    if not reference_dict:
        return ""
    
    text_parts = []
    
    text_parts.append(f"REFERENCE MATERIAL: {reference_dict['name']}")
    text_parts.append(f"Difficulty: {reference_dict['difficulty']} | Estimated Nodes: {reference_dict['estimated_nodes']}")
    text_parts.append("")
    
    text_parts.append("KEY TECHNIQUES:")
    for technique in reference_dict['key_techniques']:
        text_parts.append(f"• {technique}")
    text_parts.append("")
    
    text_parts.append("REQUIRED NODES:")
    for node in reference_dict['key_nodes']:
        text_parts.append(f"• {node}")
    text_parts.append("")
    
    if reference_dict['parameters']:
        text_parts.append("CRITICAL PARAMETERS:")
        for key, value in reference_dict['parameters'].items():
            text_parts.append(f"• {key}: {value}")
        text_parts.append("")
    
    if reference_dict['color_palette']:
        text_parts.append("COLOR PALETTE:")
        for color_name, rgba in reference_dict['color_palette'].items():
            text_parts.append(f"• {color_name}: {rgba}")
        text_parts.append("")
    
    if reference_dict.get('connection_pattern'):
        text_parts.append("CONNECTION PATTERN:")
        text_parts.append(reference_dict['connection_pattern'])
        text_parts.append("")
    
    if reference_dict.get('critical_socket_warnings'):
        text_parts.append(reference_dict['critical_socket_warnings'])
        text_parts.append("")
    
    if reference_dict['tips']:
        text_parts.append("CRITICAL TIPS:")
        for tip in reference_dict['tips']:
            text_parts.append(f"• {tip}")
    
    return "\n".join(text_parts)


# ============================================================================
# UTILITY FUNCTIONS
# ============================================================================

def get_statistics() -> Dict:
    """
    Get statistics about the reference library
    
    Returns:
        Dict with statistics
    """
    total_refs = len(MATERIAL_REFERENCES)
    all_tags = get_all_tags()
    
    difficulties = {}
    for ref in MATERIAL_REFERENCES.values():
        diff = ref['difficulty']
        difficulties[diff] = difficulties.get(diff, 0) + 1
    
    return {
        "total_references": total_refs,
        "total_unique_tags": len(all_tags),
        "all_tags": all_tags,
        "by_difficulty": difficulties
    }


if __name__ == "__main__":
    # Test the functions
    print("=== Material Reference Library ===\n")
    
    stats = get_statistics()
    print(f"Total References: {stats['total_references']}")
    print(f"Unique Tags: {stats['total_unique_tags']}")
    print(f"Tags: {', '.join(stats['all_tags'])}")
    print(f"\nBy Difficulty: {stats['by_difficulty']}\n")
    
    print("=== All References ===")
    for mat_id, name, diff in list_all_references():
        print(f"  [{diff}] {name} (ID: {mat_id})")
    
    print("\n=== Example: Cardboard Reference ===")
    print(get_reference_summary("cardboard_damaged"))
    
    print("\n=== Search: 'water' ===")
    results = search_references("water")
    for mat_id, ref in results:
        print(f"  - {ref['name']}")
