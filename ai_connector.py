"""
Blender AI Procedural Material Generator
AI Connector - Handle komunikasi dengan Google Gemini API
"""

import json
from . import prompt_templates
from . import utils
from . import material_schema
from . import material_references
from pydantic import ValidationError


# Global variable untuk store API key, client, dan model
_api_key = None
_client = None  # google-genai Client instance
_model = None  # Current model name (single model, NO fallback list)


def init_api(api_key, preferred_model='gemini-2.5-flash'):
    """
    Initialize Gemini API dengan user's API key
    
    Args:
        api_key (str): Google Gemini API key
        preferred_model (str): Model to use (gemini-3-pro-preview, gemini-3-flash-preview, gemini-2.5-pro, gemini-2.5-flash)
        
    Returns:
        bool: True if successful, False otherwise
    """
    global _api_key, _model, _client
    
    if not utils.validate_api_key(api_key):
        print("[AI Connector] Invalid API key format")
        return False
    
    try:
        from google import genai
        from google.genai import types
        
        # Available models (for validation only, NO auto-fallback)
        AVAILABLE_MODELS = [
            'gemini-3-pro-preview',    # Paid tier (preview model)
            'gemini-3-flash-preview',  # Paid tier (preview model)
            'gemini-2.5-pro',          # Paid tier
            'gemini-2.5-flash',        # FREE tier - Recommended (default)
        ]
        
        # Validate preferred model
        if preferred_model not in AVAILABLE_MODELS:
            print(f"[AI Connector] Invalid model '{preferred_model}', using default gemini-2.5-flash")
            preferred_model = 'gemini-2.5-flash'
        
        _api_key = api_key  # Store API key
        
        print(f"[AI Connector] Initializing with model: {preferred_model}")
        
        # Initialize client and model
        try:
            # Initialize client (google-genai SDK)
            client = genai.Client(api_key=api_key)
            
            # Test model availability by getting model info
            model_info = client.models.get(model=preferred_model)
            
            # Store client and model globally
            _client = client
            _model = preferred_model
            
            print(f"[AI Connector] ✓ API initialized successfully")
            print(f"[AI Connector] ✓ Using model: {preferred_model}")
            return True
            
        except Exception as e:
            error_msg = str(e)
            print(f"[AI Connector] ✗ Error initializing model '{preferred_model}': {error_msg}")
            
            # Provide helpful error messages
            if "401" in error_msg or "403" in error_msg or "unauthorized" in error_msg.lower():
                print(f"[AI Connector] 💡 This model may require paid tier API key")
            elif "404" in error_msg or "not found" in error_msg.lower():
                print(f"[AI Connector] 💡 Model not found. Please check model name.")
            
            return False
    
    except ImportError as import_err:
        print(f"[AI Connector] ERROR: google-genai library not found!")
        print(f"[AI Connector] Details: {str(import_err)}")
        print("Please run install_dependencies.bat to install google-genai SDK")
        return False
    except Exception as e:
        print(f"[AI Connector] Error initializing API: {str(e)}")
        return False


# _try_next_model() REMOVED - No auto-fallback system
# User must manually select different model from panel if quota exceeded


def get_current_model_name():
    """
    Get nama model yang sedang digunakan
    
    Returns:
        str: Nama model atau None jika belum initialized
    """
    global _model
    return _model  # _model is now a string (model name)


def enhance_prompt_with_references(user_prompt):
    """
    Find relevant reference materials for user prompt
    
    Args:
        user_prompt (str): Original user prompt
        
    Returns:
        tuple: (user_prompt, reference_dict) where reference_dict is from format_reference_for_ai()
               or (user_prompt, None) if no match found
    """
    try:
        # Extract keywords dari prompt (simple approach)
        prompt_lower = user_prompt.lower()
        
        # Search for matching references
        # Try exact match first, then fuzzy search
        matches = material_references.search_references(query=user_prompt)
        
        if not matches:
            # Try individual keywords
            keywords = [
                # Paper/packaging
                'cardboard', 'paper', 'box',
                # Liquids
                'water', 'liquid', 'ocean', 'glass', 'air',  # Added 'air' as water in Indonesian
                # Metals
                'metal', 'brushed', 'aluminum', 'steel', 'chrome', 'iron',
                # Wood
                'wood', 'timber', 'grain', 'oak', 'pine', 'plank',
                # Fabric
                'fabric', 'cloth', 'textile', 'cotton', 'velvet', 'silk'
            ]
            for keyword in keywords:
                if keyword in prompt_lower:
                    matches = material_references.search_references(query=keyword)
                    if matches:
                        break
        
        if matches:
            # Get best match (first result)
            ref_id, ref = matches[0]
            
            print(f"[AI Connector] 🎯 Found matching reference: {ref['name']}")
            print(f"[AI Connector] 📚 Will inject reference pattern into system prompt...")
            
            # Determine if we should include full pattern
            # Full pattern for very specific materials
            include_full = len(matches) == 1 and any(
                keyword in prompt_lower 
                for keyword in ref['tags'][:3]  # Check top 3 tags
            )
            
            # Get reference dict (not text!)
            ref_context = material_references.format_reference_for_ai(
                ref_id, 
                include_full_pattern=include_full
            )
            
            print(f"[AI Connector] ✓ Reference context prepared: {ref_id}")
            print(f"[AI Connector]   - Nodes: {len(ref_context.get('key_nodes', []))}")
            print(f"[AI Connector]   - Techniques: {len(ref_context.get('key_techniques', []))}")
            print(f"[AI Connector]   - Has pattern: {'Yes' if ref_context.get('connection_pattern') else 'No'}")
            
            return (user_prompt, ref_context)
        else:
            print(f"[AI Connector] No matching reference found for: {user_prompt[:50]}...")
            return (user_prompt, None)
            
    except Exception as e:
        print(f"[AI Connector] Error enhancing prompt with references: {str(e)}")
        import traceback
        traceback.print_exc()
        # Return original prompt on error
        return (user_prompt, None)


def auto_enhance_creativity(user_prompt):
    """
    AUTO-ENHANCE simple prompts menjadi detailed creative descriptions
    untuk mendorong AI generate material yang lebih complex dan realistic
    
    Args:
        user_prompt (str): Simple user input seperti "wood", "metal", "stone"
        
    Returns:
        str: Enhanced detailed prompt dengan creative additions
    """
    prompt_lower = user_prompt.lower()
    
    # Enhancement templates untuk berbagai material types
    enhancements = {
        # Wood materials
        'wood': "detailed wood texture with natural grain patterns, 3-4 brown color variations (dark to light), subtle scratches and weathering marks, slight roughness variation across surface, visible wood knots and imperfections, aged appearance with character",
        'kayu': "tekstur kayu detail dengan pola serat kayu natural, 3-4 variasi warna coklat (gelap ke terang), goresan halus dan tanda cuaca, variasi roughness di permukaan, terlihat mata kayu dan ketidaksempurnaan, tampilan aged dengan karakter",
        'bark': "detailed tree bark texture with deep grooves and ridges, 3-4 color variations (dark brown to gray), moss and lichen patches, vertical crack patterns, rough bumpy surface with displacement, weathered outer layers revealing inner bark",
        'kulit pohon': "tekstur kulit pohon detail dengan alur dan ridge dalam, 3-4 variasi warna (coklat gelap ke abu-abu), bercak lumut, pola retak vertikal, permukaan kasar bergelombang dengan displacement, lapisan luar weathered menampilkan kulit dalam",
        'bark pohon': "tekstur kulit pohon detail dengan alur dan ridge dalam, 3-4 variasi warna (coklat gelap ke abu-abu), bercak lumut, pola retak vertikal, permukaan kasar bergelombang dengan displacement, lapisan luar weathered menampilkan kulit dalam",
        
        # Metal materials  
        'metal': "realistic metal surface with brushed directional scratches, 3-4 subtle color variations from oxidation and use, anisotropic reflections, fingerprint smudges and handling marks, edge wear revealing bare metal, micro-scratches and surface imperfections",
        'aluminum': "brushed aluminum with linear scratch patterns, silver-gray base color with subtle blue-white highlights, anisotropic reflection streaks, oxidation spots with darker gray patches, fingerprint marks, edge wear with brightness variation",
        'steel': "polished steel surface with mirror-like reflections, subtle blue-gray metallic tint, micro-scratches from handling, smudge marks and fingerprints, edge wear with slight rust tint, heat discoloration zones with color variation",
        'iron': "industrial iron surface with rough texture, dark gray base with rust orange-brown patches, pitted surface with corrosion spots, 3-4 color layers (dark metal, rust, old paint), heavy wear on edges and high points, aged weathered appearance",
        'rusty': "heavily rusted metal with 4-5 color variations (deep red-brown rust, orange surface rust, dark pitting, exposed metal patches), flaking rust texture, corrosion depth with displacement, rust streaks flowing down, aged industrial look",
        
        # Stone materials
        'stone': "natural stone surface with 3-4 color variations, cracks and fracture lines, weathered pitted texture, moss and lichen growth in crevices, rough uneven surface with bump mapping, mineral deposits and color streaks",
        'concrete': "rough concrete texture with 4-5 gray color variations (dark to light), visible aggregate particles, subtle cracks and wear patterns, stains and discoloration patches, porous surface texture with fine bumps, industrial weathered appearance",
        'brick': "detailed brick wall with individual brick texture, 3-4 red-orange color variations per brick, visible mortar lines with gray color, surface weathering and erosion, moss growth in joints, slight unevenness and chipped edges",
        'batu': "permukaan batu natural dengan 3-4 variasi warna, retakan dan garis fracture, tekstur berlubang weathered, pertumbuhan lumut di celah, permukaan kasar tidak rata dengan bump mapping, deposit mineral dan garis warna",
        
        # Fabric & Organic
        'fabric': "woven fabric texture with visible thread pattern, 3-4 subtle color variations from wear, micro-fiber detail with bump mapping, slight fuzz on surface, worn areas with color fading, creases and fold patterns",
        'leather': "natural leather surface with grain pattern, 3-4 brown color variations, subtle wrinkles and creases, worn shiny areas from use, scratches and scuff marks, aged patina with character",
        'skin': "realistic skin texture with pores and micro-details, subtle color variations (undertones and surface tones), fine wrinkles and texture lines, subsurface scattering for translucency, natural irregularities and character",
        
        # Liquids & Transparent
        'water': "detailed water surface with layered wave patterns, dynamic ripples and foam on peaks, 3-4 blue-green color variations based on depth, caustic light patterns preparation, proper refraction with IOR 1.333, volumetric depth absorption, realistic flow and movement",
        'air': "detail permukaan air dengan pola gelombang berlapis, riak dinamis dan busa di puncak, 3-4 variasi warna biru-hijau berdasarkan kedalaman, preparasi pola cahaya caustic, refraksi proper dengan IOR 1.333, absorpsi kedalaman volumetrik, aliran realistis",
        'glass': "crystal clear glass with proper refraction, subtle blue-green tint, surface imperfections and tiny bubbles, fingerprint smudges, micro-scratches visible in certain angles, edge thickness variation, caustic light focusing",
        
        # Ground & Terrain
        'dirt': "earth ground texture with 4-5 brown color variations, small pebbles and debris, compressed areas and loose soil, moisture variation with darker patches, plant roots and organic matter, uneven bumpy surface",
        'mud': "wet muddy surface with glossy and matte areas, 3-4 brown color variations (dark wet to light dry), cracked dry sections, water puddles reflecting light, footprints and disturbances, organic debris mixed in",
        'sand': "fine sand texture with individual grain detail, 3-4 beige-tan color variations, subtle ripple patterns from wind, slight moisture darkening in areas, small shell fragments and debris, realistic granular appearance",
        
        # Painted & Artificial
        'paint': "painted surface with 2-3 paint layers visible, base color with chips revealing undercoat, brush stroke texture patterns, wear and scratching on edges, fading from sun exposure, slight gloss variation",
        'plastic': "injection-molded plastic surface texture with subtle flow lines, 2-3 color variations from UV fading, scratches and scuff marks from use, slight texture grain pattern, worn shiny areas from handling, matte to semi-gloss variation",
        'rubber': "textured rubber surface with 2-3 color variations, raised grip pattern with displacement, wear smooth areas, dust and dirt accumulation in grooves, slight shine variation from use, flexibility creasing marks"
    }
    
    # Check untuk exact matches atau partial matches
    enhanced_prompt = user_prompt
    
    # Exact match check
    for keyword, enhancement in enhancements.items():
        if prompt_lower == keyword or prompt_lower == f"{keyword} texture" or prompt_lower == f"material {keyword}":
            enhanced_prompt = enhancement
            print(f"[AI Connector] 🎨 Creative Enhancement: '{user_prompt}' → (detailed {keyword} description)")
            return enhanced_prompt
    
    # Partial match check (jika prompt mengandung keyword)
    for keyword, enhancement in enhancements.items():
        if keyword in prompt_lower and len(user_prompt.split()) <= 3:  # Only enhance short prompts
            # Gabungkan original prompt dengan enhancement
            enhanced_prompt = f"{user_prompt} - {enhancement}"
            print(f"[AI Connector] 🎨 Creative Enhancement: Added detailed description for '{keyword}'")
            return enhanced_prompt
    
    # Jika tidak ada match, tambahkan generic enhancement untuk prompt pendek
    if len(user_prompt.split()) <= 2:
        enhanced_prompt = f"{user_prompt} with realistic detail, 3-4 color variations, surface texture depth with bump mapping, natural imperfections and character, worn areas and weathering, layered complexity for photorealism"
        print(f"[AI Connector] 🎨 Creative Enhancement: Added generic detail enhancement")
    
    return enhanced_prompt


def validate_and_clean_material_config(config):
    """
    Validate and clean material config to prevent common AI errors
    
    Args:
        config (dict): Material config from AI
        
    Returns:
        dict: Cleaned config
    """
    if not isinstance(config, dict):
        return config
    
    nodes = config.get('nodes', [])
    total_nodes = len(nodes)
    
    cleaned_count = 0
    
    for node_idx, node in enumerate(nodes):
        if 'inputs' not in node or not isinstance(node.get('inputs'), dict):
            continue
            
        node_type = node.get('type', 'Unknown')
        inputs_to_remove = []
        
        for input_name, value in node['inputs'].items():
            needs_cleaning = False
            new_value = value
            
            # Check 1: Array too long (likely node indices)
            if isinstance(value, (list, tuple)) and len(value) > 10:
                print(f"[AI Connector] ⚠️ Cleaning node[{node_idx}] ({node_type}): '{input_name}' has {len(value)} elements (invalid!)")
                needs_cleaning = True
                
                # Try to salvage by using appropriate default or first few elements
                input_lower = input_name.lower()
                if 'color' in input_lower:
                    new_value = [0.8, 0.8, 0.8, 1.0]  # Default gray
                    print(f"[AI Connector]   → Replaced with default color")
                elif any(kw in input_lower for kw in ['vector', 'normal', 'scale', 'location', 'rotation']):
                    new_value = [0.0, 0.0, 0.0]  # Default vector
                    print(f"[AI Connector]   → Replaced with default vector")
                else:
                    # Assume float socket, use first element
                    new_value = float(value[0]) if len(value) > 0 else 0.0
                    print(f"[AI Connector]   → Using first element as float: {new_value}")
            
            # Check 2: String marker values
            elif isinstance(value, str) and value.lower() in ['must_connect', 'connect', 'link', 'from_node']:
                print(f"[AI Connector] ℹ️  Removing node[{node_idx}] ({node_type}): '{input_name}' = '{value}' (will connect via links)")
                inputs_to_remove.append(input_name)
                continue
            
            # Apply cleaning if needed
            if needs_cleaning:
                node['inputs'][input_name] = new_value
                cleaned_count += 1
        
        # Remove invalid inputs
        for input_name in inputs_to_remove:
            del node['inputs'][input_name]
            cleaned_count += 1
    
    if cleaned_count > 0:
        print(f"[AI Connector] ✓ Cleaned {cleaned_count} invalid input value(s)")
    
    return config


def generate_material_config(user_prompt, prompt_history=None, current_material_config=None):
    """
    Generate material configuration dari user prompt menggunakan AI
    Supports [CONTINUE] for complex materials
    
    Args:
        user_prompt (str): User's material description
        prompt_history (list): Previous prompts untuk context
        current_material_config (dict): Current material untuk modification
        
    Returns:
        dict: Material configuration atau None jika gagal
    """
    global _model
    
    # Check internet connection
    if not utils.check_internet_connection():
        print("[AI Connector] No internet connection")
        return None
    
    # Check API initialized
    if _model is None:
        print("[AI Connector] API not initialized")
        return None
    
    # ========================================================================
    # AUTO-ENHANCE CREATIVITY (NEW!)
    # ========================================================================
    # Enhance simple prompts menjadi detailed creative descriptions
    # Hanya untuk new materials, not modifications
    if current_material_config is None and not prompt_history:
        original_prompt = user_prompt
        user_prompt = auto_enhance_creativity(user_prompt)
        if user_prompt != original_prompt:
            print(f"[AI Connector] 💡 Original: '{original_prompt}'")
            print(f"[AI Connector] ✨ Enhanced: '{user_prompt[:100]}...'")
    
    # ========================================================================
    # AUTO-ENHANCE PROMPT WITH MATERIAL REFERENCES
    # ========================================================================
    # Only enhance if this is a new material (not a modification)
    reference_context = None
    if current_material_config is None:
        user_prompt, reference_context = enhance_prompt_with_references(user_prompt)
        if reference_context:
            print(f"[AI Connector] ✓ Using reference: {reference_context['name']}")
    else:
        print("[AI Connector] Skipping reference enhancement (modifying existing material)")
    
    # Initial request - pass reference_context
    result = _generate_single_request(user_prompt, prompt_history, current_material_config, reference_context)
    
    # Handle tuple response dengan user message (config, error_type, user_message)
    if isinstance(result, tuple):
        if len(result) == 3:
            config, error_type, user_message = result
            if config is None:
                return (None, error_type, user_message)  # Pass user message to operator
        elif len(result) == 2:
            # Backward compatibility
            config, error_type = result
            if config is None:
                return (None, error_type, None)
        else:
            config = result[0] if result else None
            if config is None:
                return (None, 'unknown_error', None)
    else:
        # Direct config (legacy)
        config = result
        if config is None:
            return (None, 'unknown_error', None)
    
    # Check if response was truncated and needs continuation
    if config and config.get('_needs_continue'):
        print("[AI Connector] Response truncated, requesting continuation...")
        
        # Get continuation
        continuation_config = _generate_continuation(user_prompt, prompt_history, config)
        
        if continuation_config:
            # Merge configurations
            config = _merge_configs(config, continuation_config)
            print("[AI Connector] Successfully merged continuation")
    
    # Clean internal flags
    if config:
        config.pop('_needs_continue', None)
        config.pop('_partial_response', None)
    
    return (config, None, None)  # Return tuple (config, None, None) untuk sukses


def _generate_single_request(user_prompt, prompt_history, current_material_config, reference_context=None):
    """
    Single API request - NO FALLBACK, show clear error messages
    
    Args:
        reference_context: Dict dari format_reference_for_ai() atau None
    """
    global _client, _model
    
    current_model = get_current_model_name()
    print(f"[AI Connector] Using model: {current_model}")
    
    try:
        # Build full prompt dengan context DAN reference
        full_prompt = prompt_templates.build_context_aware_prompt(
            user_prompt,
            prompt_history or [],
            current_material_config,
            reference_context=reference_context  # Pass reference context!
        )
        
        print(f"[AI Connector] Sending prompt to Gemini API...")
        
        # Generate response with google-genai Client API
        from google.genai import types
        
        response = _client.models.generate_content(
            model=_model,  # Model name as string
            contents=full_prompt,
            config=types.GenerateContentConfig(
                temperature=0.7,
                top_p=0.95,
                top_k=40,
                max_output_tokens=8192,  # Gemini 2.5/3 models support up to 8192
                response_mime_type='application/json',
            )
        )
        
        # Extract text response
        response_text = response.text.strip()
        
        print(f"[AI Connector] Received response ({len(response_text)} chars)")
        
        # Parse JSON and validate
        try:
            raw_json = json.loads(response_text)
            print(f"[AI Connector] Parsed JSON successfully")
            
            # AUTO-UNWRAP: Jika response adalah list dengan 1 element, extract element tersebut
            # Gemini kadang return [{...}] bukan {...}
            if isinstance(raw_json, list):
                if len(raw_json) == 1 and isinstance(raw_json[0], dict):
                    print(f"[AI Connector] ⚠️ Response is array with 1 element, auto-unwrapping...")
                    raw_json = raw_json[0]  # Extract first element
                    print(f"[AI Connector] ✓ Successfully unwrapped to dict")
                elif len(raw_json) == 0:
                    print(f"[AI Connector] ❌ Response is empty array")
                    user_message = "AI returned empty response. Please try again."
                    return (None, 'invalid_format', user_message)
                else:
                    print(f"[AI Connector] ❌ Response is array with {len(raw_json)} elements (expected single object)")
                    print(f"[AI Connector] Response content (first 500 chars): {str(raw_json)[:500]}")
                    user_message = "AI returned multiple materials. Expected single material. Please try again."
                    return (None, 'invalid_format', user_message)
            
            # Validasi tipe data - harus dict setelah unwrapping
            if not isinstance(raw_json, dict):
                print(f"[AI Connector] ❌ Invalid response type: expected dict/object, got {type(raw_json).__name__}")
                print(f"[AI Connector] Response content (first 500 chars): {str(raw_json)[:500]}")
                user_message = "AI returned invalid format. Expected material configuration object. Please try again."
                return (None, 'invalid_format', user_message)
            
            
            print(f"[AI Connector] - material_name: {raw_json.get('material_name', 'N/A')}")
            
            # Validasi nodes
            if 'nodes' not in raw_json:
                print(f"[AI Connector] ❌ Missing 'nodes' field in response")
                user_message = "AI response missing nodes definition. Please try again."
                return (None, 'invalid_format', user_message)
            
            if not isinstance(raw_json['nodes'], list):
                print(f"[AI Connector] ❌ Invalid 'nodes' type: expected list, got {type(raw_json['nodes']).__name__}")
                user_message = "AI returned invalid nodes format. Please try again."
                return (None, 'invalid_format', user_message)
            
            print(f"[AI Connector] - nodes count: {len(raw_json.get('nodes', []))}")
            
            # Validasi links
            if 'links' not in raw_json:
                print(f"[AI Connector] ❌ Missing 'links' field in response")
                user_message = "AI response missing links definition. Please try again."
                return (None, 'invalid_format', user_message)
            
            print(f"[AI Connector] - links count: {len(raw_json.get('links', []))}")
            
            
            # Debug first few links to see format
            if raw_json.get('links'):
                # Validasi bahwa links adalah list of dict
                if not isinstance(raw_json['links'], list):
                    print(f"[AI Connector] ❌ Invalid 'links' type: expected list, got {type(raw_json['links']).__name__}")
                    user_message = "AI returned invalid links format. Please try again."
                    return (None, 'invalid_format', user_message)
                
                # Validasi elemen pertama adalah dict
                if len(raw_json['links']) > 0:
                    first_link = raw_json['links'][0]
                    if not isinstance(first_link, dict):
                        print(f"[AI Connector] ❌ Invalid link element type: expected dict, got {type(first_link).__name__}")
                        print(f"[AI Connector] Link content: {first_link}")
                        user_message = "AI returned invalid link format. Expected connection objects. Please try again."
                        return (None, 'invalid_format', user_message)
                    
                    print(f"[AI Connector] - First link example: {first_link}")
                    # Check if using integers or strings
                    from_node_type = type(first_link.get('from_node')).__name__
                    to_node_type = type(first_link.get('to_node')).__name__
                    print(f"[AI Connector] - from_node type: {from_node_type}, to_node type: {to_node_type}")
            
            # Validate dengan Pydantic - provides structure validation!
            try:
                material = material_schema.validate_material_config(raw_json)
                config = material_schema.material_config_to_dict(material)
                
                # Clean invalid input values before passing to material_generator
                config = validate_and_clean_material_config(config)
                
                print(f"[AI Connector] ✓ Successfully validated material with {current_model}: {config.get('material_name')}")
                print(f"[AI Connector] ✓ Contains {len(config.get('nodes', []))} nodes, {len(config.get('links', []))} links")
                return (config, None, None)  # Success - (config, None, None)
            except ValidationError as e:
                print(f"[AI Connector] Validation error: {e}")
                print("[AI Connector] Response did not match schema requirements")
                user_message = "Material generation failed validation. Please try again with a simpler prompt."
                return (None, 'validation_error', user_message)
                
        except json.JSONDecodeError as e:
            print(f"[AI Connector] JSON decode error: {e}")
            print(f"[AI Connector] Response text (first 500 chars): {response_text[:500]}")
            
            # Check if response was truncated
            truncated = False
            if len(response_text) < 1500:  # Too short for a complete material config
                print(f"[AI Connector] ⚠ Response seems truncated (only {len(response_text)} chars)")
                truncated = True
            elif not response_text.endswith('}'):  # JSON should end with }
                print(f"[AI Connector] ⚠ Response doesn't end with '}}', likely truncated")
                truncated = True
            
            if truncated:
                user_message = "Response was truncated. Try using a simpler prompt or starting over."
            else:
                user_message = "Failed to parse AI response. Please try again."
            
            return (None, 'json_parse_error', user_message)
            
    except Exception as e:
        error_msg = str(e)
        print(f"[AI Connector] ❌ Error with {current_model}: {error_msg}")
        
        # Check error type and return appropriate message
        if "429" in error_msg or "quota" in error_msg.lower() or "resource" in error_msg.lower():
            error_type = 'quota_exceeded'
            user_message = f"Model '{current_model}' quota exceeded. Please try another model or wait until quota resets."
            print(f"[AI Connector] 💡 {user_message}")
        elif "401" in error_msg or "403" in error_msg or "unauthorized" in error_msg.lower():
            error_type = 'unauthorized'
            user_message = f"Model '{current_model}' requires paid tier. Please upgrade your API key or select a free tier model."
            print(f"[AI Connector] 💡 {user_message}")
        else:
            error_type = 'api_error'
            user_message = f"Error with model '{current_model}': {error_msg[:100]}"
            print(f"[AI Connector] 💡 {user_message}")
        
        return (None, error_type, user_message)


def _generate_continuation(user_prompt, prompt_history, partial_config):
    """Generate continuation for truncated response"""
    global _model
    
    try:
        # Build continuation prompt
        continue_prompt = f"""Continue from where you left off.

Previous partial response received:
- Material name: {partial_config.get('material_name', 'Unknown')}
- Nodes received: {len(partial_config.get('nodes', []))}
- Links received: {len(partial_config.get('links', []))}

Please provide the REMAINING nodes and links in the same JSON format.
Return ONLY: {{"nodes": [...remaining...], "links": [...remaining...]}}"""
        
        print("[AI Connector] Requesting continuation...")
        
        response = _model.generate_content(
            continue_prompt,
            generation_config={
                'temperature': 0.5,
                'top_p': 0.95,
                'top_k': 40,
                'max_output_tokens': 8192,
            }
        )
        
        response_text = response.text.strip()
        print(f"[AI Connector] Received continuation ({len(response_text)} chars)")
        
        # Parse continuation
        config = parse_ai_response(response_text)
        return config
        
    except Exception as e:
        print(f"[AI Connector] Error getting continuation: {str(e)}")
        return None


def _merge_configs(original, continuation):
    """Merge original and continuation configs"""
    if not continuation:
        return original
    
    merged = original.copy()
    
    # Merge nodes
    if 'nodes' in continuation:
        existing_nodes = merged.get('nodes', [])
        new_nodes = continuation['nodes']
        
        # Adjust node indices in continuation links
        offset = len(existing_nodes)
        
        merged['nodes'] = existing_nodes + new_nodes
        print(f"[AI Connector] Merged {len(new_nodes)} additional nodes")
    
    # Merge links with index adjustment
    if 'links' in continuation:
        existing_links = merged.get('links', [])
        new_links = continuation['links']
        
        # Adjust indices if nodes were added
        if 'nodes' in continuation:
            for link in new_links:
                link['from_node'] += offset
                link['to_node'] += offset
        
        merged['links'] = existing_links + new_links
        print(f"[AI Connector] Merged {len(new_links)} additional links")
    
    return merged


def parse_ai_response(response_text):
    """
    Parse AI response text menjadi material configuration dict
    Detects [CONTINUE] marker for truncated responses
    
    Args:
        response_text (str): Raw AI response
        
    Returns:
        dict: Parsed configuration atau None
    """
    try:
        # Save original for error reporting
        original_text = response_text
        original_length = len(response_text)
        
        # Check for [CONTINUE] marker
        needs_continue = '[CONTINUE]' in response_text or '[continue]' in response_text.lower()
        
        # Remove continuation marker if present
        response_text = response_text.replace('[CONTINUE]', '').replace('[continue]', '')
        
        # With structured output, we expect clean JSON (no markdown blocks)
        # But still clean just in case
        response_text = response_text.strip()
        
        if response_text.startswith('```json'):
            response_text = response_text[7:]  # Remove ```json
            if '```' in response_text:
                response_text = response_text[:response_text.rfind('```')]
        elif response_text.startswith('```'):
            response_text = response_text[3:]  # Remove ```
            if '```' in response_text:
                response_text = response_text[:response_text.rfind('```')]
        
        response_text = response_text.strip()
        
        # Structured output should already be valid JSON - no fixing needed!
        # If truncated, schema validation will fail and we return None
        
        # Parse JSON
        config = json.loads(response_text)
        
        # Validate structure
        if not isinstance(config, dict):
            print("[AI Connector] Response is not a dict")
            return None
        
        if 'nodes' not in config or 'links' not in config:
            print("[AI Connector] Missing required fields (nodes/links)")
            return None
        
        if not isinstance(config['nodes'], list) or not isinstance(config['links'], list):
            print("[AI Connector] nodes or links is not a list")
            return None
        
        # With structured output, continuation not needed
        # Schema ensures complete response
        
        # Validate minimal nodes (harus ada Output node)
        has_output = any(
            node.get('type') == 'ShaderNodeOutputMaterial' 
            for node in config['nodes']
        )
        
        if not has_output:
            print("[AI Connector] No output node found, adding one")
            # Add output node
            config['nodes'].append({
                "type": "ShaderNodeOutputMaterial",
                "location": [300, 0],
                "inputs": {}
            })
        
        return config
        
    except json.JSONDecodeError as e:
        print(f"[AI Connector] JSON parse error: {str(e)}")
        print(f"[AI Connector] Cleaned text (first 500 chars): {response_text[:500]}")
        print(f"[AI Connector] Original response: {original_text}")
        return None
    except Exception as e:
        print(f"[AI Connector] Error parsing response: {str(e)}")
        import traceback
        traceback.print_exc()
        return None


def is_api_ready():
    """
    Check apakah AI API sudah ready untuk digunakan
    
    Returns:
        bool: True if ready, False otherwise
    """
    global _client, _api_key
    return _client is not None and _api_key is not None
