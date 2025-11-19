"""
Database initialization script.
Run this to create the database and optionally add sample data.
"""
from database import init_db, SessionLocal
from models import Dream, Location, Entity, LayerEnum, EntityTypeEnum
from datetime import datetime, timedelta
import crud
import schemas

def create_sample_data():
    """Create sample dreams and locations for testing"""
    db = SessionLocal()
    
    try:
        print("Creating sample data...")
        
        # Sample dreams
        dreams_data = [
            {
                "date": datetime.now() - timedelta(days=2),
                "cycle": 1,
                "content": "I was in my childhood home. The rooms were familiar but somehow different. I walked through the garden and found a hidden door leading to a forest.",
                "language": "en"
            },
            {
                "date": datetime.now() - timedelta(days=1),
                "cycle": 1,
                "content": "I found myself in a vast library with endless shelves. Books were floating in the air. I met an old friend who handed me a glowing book.",
                "language": "en"
            },
            {
                "date": datetime.now(),
                "cycle": 1,
                "content": "I was swimming in a crystal clear ocean. Below me I could see an underwater city with lights. I dove down and entered through a grand archway.",
                "language": "en"
            },
        ]
        
        for dream_data in dreams_data:
            dream_schema = schemas.DreamCreate(**dream_data)
            dream = crud.create_dream(db, dream_schema)
            print(f"✓ Created dream: {dream.id}")
        
        # Sample locations (since AI processing would create these)
        locations_data = [
            {
                "name": "Childhood Home",
                "archetype": "home",
                "layer": LayerEnum.PRIMARY,
                "x": 0.0,
                "y": 0.0,
                "symbol": "🏠",
                "description": "Familiar yet strange childhood dwelling",
                "color": "#3b82f6",
                "frequency": 2
            },
            {
                "name": "Mystical Forest",
                "archetype": "forest",
                "layer": LayerEnum.PRIMARY,
                "x": 0.5,
                "y": 0.3,
                "symbol": "🌲",
                "description": "A mysterious forest beyond the garden",
                "color": "#22c55e",
                "frequency": 1
            },
            {
                "name": "Infinite Library",
                "archetype": "building",
                "layer": LayerEnum.UPPER,
                "x": -0.4,
                "y": -0.3,
                "symbol": "📚",
                "description": "A library with floating books",
                "color": "#8b5cf6",
                "frequency": 1
            },
            {
                "name": "Crystal Ocean",
                "archetype": "water",
                "layer": LayerEnum.PRIMARY,
                "x": 0.2,
                "y": 0.6,
                "symbol": "🌊",
                "description": "Clear waters above an underwater city",
                "color": "#06b6d4",
                "frequency": 1
            },
            {
                "name": "Underwater City",
                "archetype": "city",
                "layer": LayerEnum.LOWER,
                "x": 0.3,
                "y": 0.7,
                "symbol": "🏛️",
                "description": "A glowing city beneath the waves",
                "color": "#0ea5e9",
                "frequency": 1
            },
        ]
        
        for loc_data in locations_data:
            location = Location(**loc_data)
            db.add(location)
            db.commit()
            print(f"✓ Created location: {location.name}")
        
        # Sample entities
        entities_data = [
            {
                "name": "Old Friend",
                "type": EntityTypeEnum.PERSON,
                "symbol": "👤",
                "confidence": 0.9,
                "description": "A friend from the past"
            },
            {
                "name": "Glowing Book",
                "type": EntityTypeEnum.OBJECT,
                "symbol": "📖",
                "confidence": 1.0,
                "description": "A mysterious glowing tome"
            },
        ]
        
        for ent_data in entities_data:
            entity = Entity(**ent_data)
            db.add(entity)
            db.commit()
            print(f"✓ Created entity: {entity.name}")
        
        print("\n✅ Sample data created successfully!")
        
    except Exception as e:
        print(f"❌ Error creating sample data: {e}")
        db.rollback()
    finally:
        db.close()


if __name__ == "__main__":
    print("Initializing database...")
    init_db()
    print("✅ Database initialized!")
    
    response = input("\nCreate sample data? (y/n): ")
    if response.lower() == 'y':
        create_sample_data()
    
    print("\n🎉 Setup complete! You can now run the server.")