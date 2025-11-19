"""
OpenAI integration for dream analysis and extraction.
Handles AI-powered extraction of locations, entities, and transits from dream content.
"""
import os
import json
from typing import Dict, Any
from openai import AsyncOpenAI
from dotenv import load_dotenv
import schemas

load_dotenv()

# Initialize OpenAI client
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
OPENAI_MODEL = os.getenv("OPENAI_MODEL", "gpt-4-turbo-preview")

client = AsyncOpenAI(api_key=OPENAI_API_KEY) if OPENAI_API_KEY else None


EXTRACTION_PROMPT = """You are an expert dream analyst. Analyze the following dream and extract structured information.

Dream content:
{dream_content}

Extract the following information in JSON format:

1. **Locations**: Places visited in the dream
   - name: descriptive name
   - archetype: type of place (home, forest, city, water, cave, building, etc.)
   - layer: -1 (underworld/subconscious), 0 (normal reality), or 1 (higher realm/sky)
   - x: float between -1 and 1 (east-west position)
   - y: float between -1 and 1 (north-south position)
   - symbol: appropriate emoji (🏠 🌲 🏙️ 🌊 etc.)
   - description: brief description

2. **Entities**: People, beings, animals, objects, or abstract concepts
   - name: who/what it is
   - type: "person", "being", "animal", "abstract", or "object"
   - symbol: appropriate emoji
   - confidence: 0.0 to 1.0 (how certain you are about this entity)
   - description: brief description

3. **Transits**: Movements between locations
   - from_location: name of starting location
   - to_location: name of destination location
   - trigger: what caused the movement
   - confidence: 0.0 to 1.0

Return ONLY valid JSON in this exact format:
{{
  "locations": [
    {{"name": "...", "archetype": "...", "layer": 0, "x": 0.0, "y": 0.0, "symbol": "...", "description": "..."}}
  ],
  "entities": [
    {{"name": "...", "type": "person", "symbol": "...", "confidence": 1.0, "description": "..."}}
  ],
  "transits": [
    {{"from_location": "...", "to_location": "...", "trigger": "...", "confidence": 1.0}}
  ]
}}

Important:
- Be creative but accurate in spatial positioning
- Use meaningful archetypes
- Assign appropriate layers based on dream symbolism
- Extract all significant elements
"""


async def extract_dream_data(dream_content: str, language: str = "en") -> schemas.AIExtractionResult:
    """
    Extract structured data from dream content using OpenAI.
    Falls back to stub data if API key is not configured.
    """
    if not client or not OPENAI_API_KEY:
        # Stub response for testing without API key
        return _get_stub_extraction(dream_content)
    
    try:
        response = await client.chat.completions.create(
            model=OPENAI_MODEL,
            messages=[
                {
                    "role": "system",
                    "content": "You are a dream analysis expert. Always respond with valid JSON only."
                },
                {
                    "role": "user",
                    "content": EXTRACTION_PROMPT.format(dream_content=dream_content)
                }
            ],
            temperature=0.3,  # Low temperature for consistent extraction
            max_tokens=2000
        )
        
        # Parse response
        content = response.choices[0].message.content
        data = json.loads(content)
        
        # Convert to proper schemas
        return _parse_extraction_data(data)
    
    except Exception as e:
        print(f"OpenAI extraction error: {e}")
        # Fall back to stub on error
        return _get_stub_extraction(dream_content)


def _parse_extraction_data(data: Dict[str, Any]) -> schemas.AIExtractionResult:
    """Parse raw AI response into proper schema objects"""
    locations = []
    for loc in data.get("locations", []):
        locations.append(schemas.LocationCreate(
            name=loc["name"],
            archetype=loc.get("archetype"),
            layer=_parse_layer(loc.get("layer", 0)),
            x=float(loc.get("x", 0.0)),
            y=float(loc.get("y", 0.0)),
            symbol=loc.get("symbol"),
            description=loc.get("description"),
            color=_get_color_for_archetype(loc.get("archetype", ""))
        ))
    
    entities = []
    for ent in data.get("entities", []):
        entities.append(schemas.EntityCreate(
            name=ent["name"],
            type=_parse_entity_type(ent.get("type", "abstract")),
            symbol=ent.get("symbol"),
            confidence=float(ent.get("confidence", 1.0)),
            description=ent.get("description")
        ))
    
    transits = []
    # Transits will be resolved after locations are created
    
    return schemas.AIExtractionResult(
        locations=locations,
        entities=entities,
        transits=transits  # Empty for now, will be created separately
    )


def _parse_layer(layer_value) -> Any:
    """Convert layer value to LayerEnum"""
    from models import LayerEnum
    if isinstance(layer_value, int):
        if layer_value < 0:
            return LayerEnum.LOWER
        elif layer_value > 0:
            return LayerEnum.UPPER
        else:
            return LayerEnum.PRIMARY
    return LayerEnum.PRIMARY


def _parse_entity_type(type_str: str) -> Any:
    """Convert string to EntityTypeEnum"""
    from models import EntityTypeEnum
    type_map = {
        "person": EntityTypeEnum.PERSON,
        "being": EntityTypeEnum.BEING,
        "animal": EntityTypeEnum.ANIMAL,
        "abstract": EntityTypeEnum.ABSTRACT,
        "object": EntityTypeEnum.OBJECT
    }
    return type_map.get(type_str.lower(), EntityTypeEnum.ABSTRACT)


def _get_color_for_archetype(archetype: str) -> str:
    """Assign color based on location archetype"""
    color_map = {
        "home": "#3b82f6",      # blue
        "forest": "#22c55e",    # green
        "city": "#6366f1",      # indigo
        "water": "#06b6d4",     # cyan
        "cave": "#78716c",      # stone
        "building": "#8b5cf6",  # violet
        "sky": "#38bdf8",       # sky blue
        "underground": "#44403c" # dark gray
    }
    return color_map.get(archetype.lower(), "#3b82f6")


def _get_stub_extraction(dream_content: str) -> schemas.AIExtractionResult:
    """
    Stub function for testing without OpenAI API.
    Returns sample extraction data.
    """
    from models import LayerEnum, EntityTypeEnum
    
    # Simple extraction based on keywords
    locations = []
    entities = []
    
    # Check for common location keywords
    if any(word in dream_content.lower() for word in ["house", "home", "room"]):
        locations.append(schemas.LocationCreate(
            name="Home",
            archetype="home",
            layer=LayerEnum.PRIMARY,
            x=0.0,
            y=0.0,
            symbol="🏠",
            description="A familiar home setting",
            color="#3b82f6"
        ))
    
    if any(word in dream_content.lower() for word in ["forest", "tree", "woods"]):
        locations.append(schemas.LocationCreate(
            name="Forest",
            archetype="forest",
            layer=LayerEnum.PRIMARY,
            x=0.5,
            y=0.3,
            symbol="🌲",
            description="A mysterious forest",
            color="#22c55e"
        ))
    
    if any(word in dream_content.lower() for word in ["water", "ocean", "sea", "lake"]):
        locations.append(schemas.LocationCreate(
            name="Water",
            archetype="water",
            layer=LayerEnum.PRIMARY,
            x=-0.3,
            y=0.5,
            symbol="🌊",
            description="A body of water",
            color="#06b6d4"
        ))
    
    # Add default location if none found
    if not locations:
        locations.append(schemas.LocationCreate(
            name="Unknown Place",
            archetype="abstract",
            layer=LayerEnum.PRIMARY,
            x=0.0,
            y=0.0,
            symbol="❓",
            description="An unidentified location",
            color="#6b7280"
        ))
    
    # Check for entities
    if any(word in dream_content.lower() for word in ["person", "man", "woman", "friend", "stranger"]):
        entities.append(schemas.EntityCreate(
            name="Unknown Person",
            type=EntityTypeEnum.PERSON,
            symbol="👤",
            confidence=0.7,
            description="A person from the dream"
        ))
    
    return schemas.AIExtractionResult(
        locations=locations,
        entities=entities,
        transits=[]
    )