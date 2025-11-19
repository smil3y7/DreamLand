"""
Background task processing for async operations.
Handles dream analysis and extraction asynchronously.
"""
import asyncio
from sqlalchemy.orm import Session
from typing import Optional
import crud
import llm
import models


async def process_dream_async(dream_id: int, db: Session):
    """
    Process a dream asynchronously:
    1. Extract locations, entities, and transits using AI
    2. Create or link to existing locations/entities
    3. Update dream as processed
    """
    try:
        # Get dream
        dream = crud.get_dream(db, dream_id)
        if not dream or dream.processed:
            return
        
        # Extract data using AI
        extraction_result = await llm.extract_dream_data(dream.content, dream.language)
        
        # Process locations
        location_map = {}  # Maps extracted name to database ID
        for loc_data in extraction_result.locations:
            # Check if location already exists
            existing = crud.get_location_by_name(db, loc_data.name)
            
            if existing:
                # Increment frequency and update position (weighted average)
                weight = existing.frequency / (existing.frequency + 1)
                existing.x = existing.x * weight + loc_data.x * (1 - weight)
                existing.y = existing.y * weight + loc_data.y * (1 - weight)
                crud.increment_location_frequency(db, existing.id)
                location_map[loc_data.name] = existing.id
            else:
                # Create new location
                new_location = crud.create_location(db, loc_data)
                location_map[loc_data.name] = new_location.id
            
            # Link dream to location
            crud.link_dream_to_location(
                db, 
                dream_id=dream.id,
                location_id=location_map[loc_data.name],
                order=len(location_map)
            )
        
        # Process entities
        for ent_data in extraction_result.entities:
            # Check if entity already exists
            existing = crud.get_entity_by_name(db, ent_data.name)
            
            if existing:
                entity_id = existing.id
            else:
                # Create new entity
                new_entity = crud.create_entity(db, ent_data)
                entity_id = new_entity.id
            
            # Link dream to entity
            crud.link_dream_to_entity(db, dream_id=dream.id, entity_id=entity_id)
        
        # Process transits (if any)
        for transit_data in extraction_result.transits:
            from_id = location_map.get(transit_data.from_location_id)
            to_id = location_map.get(transit_data.to_location_id)
            
            if from_id and to_id:
                crud.create_transit(db, transit_data, dream_id=dream.id)
        
        # Mark dream as processed
        crud.update_dream_processed(db, dream_id, processed=True)
        
        print(f"Successfully processed dream {dream_id}")
        
    except Exception as e:
        print(f"Error processing dream {dream_id}: {e}")
        # Don't mark as processed if there was an error


def run_async_task(coro):
    """
    Helper to run async task in sync context.
    Used for background task execution.
    """
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    try:
        return loop.run_until_complete(coro)
    finally:
        loop.close()