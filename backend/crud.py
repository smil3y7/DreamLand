"""
CRUD operations for database entities.
Create, Read, Update, Delete functions for dreams, locations, entities, transits.
"""
from sqlalchemy.orm import Session, joinedload
from sqlalchemy import func, desc
from typing import List, Optional
from datetime import datetime
import json

import models
import schemas


# Dream CRUD
def create_dream(db: Session, dream: schemas.DreamCreate) -> models.Dream:
    """Create a new dream entry"""
    db_dream = models.Dream(
        date=dream.date,
        cycle=dream.cycle,
        content=dream.content,
        language=dream.language,
        processed=False
    )
    db.add(db_dream)
    db.commit()
    db.refresh(db_dream)
    return db_dream


def get_dream(db: Session, dream_id: int) -> Optional[models.Dream]:
    """Get a dream by ID"""
    return db.query(models.Dream).filter(models.Dream.id == dream_id).first()


def get_dreams(db: Session, skip: int = 0, limit: int = 100) -> List[models.Dream]:
    """Get all dreams with pagination"""
    return db.query(models.Dream).order_by(desc(models.Dream.date)).offset(skip).limit(limit).all()


def update_dream_processed(db: Session, dream_id: int, processed: bool = True):
    """Mark dream as processed by AI"""
    dream = get_dream(db, dream_id)
    if dream:
        dream.processed = processed
        db.commit()
        db.refresh(dream)
    return dream


# Location CRUD
def create_location(db: Session, location: schemas.LocationCreate) -> models.Location:
    """Create a new location"""
    db_location = models.Location(**location.dict())
    db.add(db_location)
    db.commit()
    db.refresh(db_location)
    return db_location


def get_location(db: Session, location_id: int) -> Optional[models.Location]:
    """Get a location by ID"""
    return db.query(models.Location).filter(models.Location.id == location_id).first()


def get_location_by_name(db: Session, name: str) -> Optional[models.Location]:
    """Get a location by name (case-insensitive)"""
    return db.query(models.Location).filter(func.lower(models.Location.name) == name.lower()).first()


def get_locations(db: Session, layer: Optional[models.LayerEnum] = None) -> List[models.Location]:
    """Get all locations, optionally filtered by layer"""
    query = db.query(models.Location)
    if layer:
        query = query.filter(models.Location.layer == layer)
    return query.all()


def update_location(db: Session, location_id: int, location_update: schemas.LocationUpdate) -> Optional[models.Location]:
    """Update a location"""
    db_location = get_location(db, location_id)
    if not db_location:
        return None
    
    update_data = location_update.dict(exclude_unset=True)
    for key, value in update_data.items():
        setattr(db_location, key, value)
    
    db_location.updated_at = datetime.utcnow()
    db.commit()
    db.refresh(db_location)
    return db_location


def increment_location_frequency(db: Session, location_id: int):
    """Increment frequency counter for a location"""
    location = get_location(db, location_id)
    if location:
        location.frequency += 1
        db.commit()


def merge_locations(db: Session, source_ids: List[int], target_name: str, user_note: Optional[str] = None) -> models.Location:
    """
    Merge multiple locations into one.
    Creates changelog entry and updates all relationships.
    """
    sources = [get_location(db, lid) for lid in source_ids]
    sources = [s for s in sources if s]  # Filter out None values
    
    if not sources:
        raise ValueError("No valid source locations found")
    
    # Create new merged location with averaged position
    avg_x = sum(s.x for s in sources) / len(sources)
    avg_y = sum(s.y for s in sources) / len(sources)
    total_frequency = sum(s.frequency for s in sources)
    
    merged_location = models.Location(
        name=target_name,
        archetype=sources[0].archetype,
        layer=sources[0].layer,
        x=avg_x,
        y=avg_y,
        symbol=sources[0].symbol,
        color=sources[0].color,
        frequency=total_frequency,
        description=f"Merged from: {', '.join(s.name for s in sources)}"
    )
    db.add(merged_location)
    db.flush()
    
    # Update all references to point to merged location
    for source in sources:
        # Update dream_locations
        db.query(models.DreamLocation).filter(
            models.DreamLocation.location_id == source.id
        ).update({"location_id": merged_location.id})
        
        # Update entities
        db.query(models.Entity).filter(
            models.Entity.location_id == source.id
        ).update({"location_id": merged_location.id})
        
        # Update transits
        db.query(models.Transit).filter(
            models.Transit.from_location_id == source.id
        ).update({"from_location_id": merged_location.id})
        
        db.query(models.Transit).filter(
            models.Transit.to_location_id == source.id
        ).update({"to_location_id": merged_location.id})
    
    # Create changelog entry
    changelog = models.ChangeLog(
        action=models.ChangeActionEnum.MERGE,
        entity_type="location",
        entity_id=merged_location.id,
        old_data=None,
        new_data={"name": target_name, "x": avg_x, "y": avg_y},
        merged_from=source_ids,
        user_note=user_note
    )
    db.add(changelog)
    
    # Delete source locations
    for source in sources:
        db.delete(source)
    
    db.commit()
    db.refresh(merged_location)
    return merged_location


# Entity CRUD
def create_entity(db: Session, entity: schemas.EntityCreate) -> models.Entity:
    """Create a new entity"""
    db_entity = models.Entity(**entity.dict())
    db.add(db_entity)
    db.commit()
    db.refresh(db_entity)
    return db_entity


def get_entity(db: Session, entity_id: int) -> Optional[models.Entity]:
    """Get an entity by ID"""
    return db.query(models.Entity).filter(models.Entity.id == entity_id).first()


def get_entity_by_name(db: Session, name: str) -> Optional[models.Entity]:
    """Get an entity by name (case-insensitive)"""
    return db.query(models.Entity).filter(func.lower(models.Entity.name) == name.lower()).first()


def get_entities(db: Session, location_id: Optional[int] = None) -> List[models.Entity]:
    """Get all entities, optionally filtered by location"""
    query = db.query(models.Entity)
    if location_id:
        query = query.filter(models.Entity.location_id == location_id)
    return query.all()


# Transit CRUD
def create_transit(db: Session, transit: schemas.TransitCreate, dream_id: int) -> models.Transit:
    """Create a new transit"""
    db_transit = models.Transit(
        dream_id=dream_id,
        **transit.dict()
    )
    db.add(db_transit)
    db.commit()
    db.refresh(db_transit)
    return db_transit


def get_transits_for_location(db: Session, location_id: int) -> List[models.Transit]:
    """Get all transits from or to a location"""
    return db.query(models.Transit).filter(
        (models.Transit.from_location_id == location_id) |
        (models.Transit.to_location_id == location_id)
    ).all()


# Link dreams to extracted data
def link_dream_to_location(db: Session, dream_id: int, location_id: int, order: int = 0):
    """Link a dream to a location"""
    link = models.DreamLocation(dream_id=dream_id, location_id=location_id, order=order)
    db.add(link)
    db.commit()


def link_dream_to_entity(db: Session, dream_id: int, entity_id: int):
    """Link a dream to an entity"""
    link = models.DreamEntity(dream_id=dream_id, entity_id=entity_id)
    db.add(link)
    db.commit()


# Stats and export
def get_world_stats(db: Session) -> schemas.WorldStats:
    """Get statistics about the dream world"""
    total_dreams = db.query(func.count(models.Dream.id)).scalar()
    total_locations = db.query(func.count(models.Location.id)).scalar()
    total_entities = db.query(func.count(models.Entity.id)).scalar()
    total_transits = db.query(func.count(models.Transit.id)).scalar()
    
    most_frequent = db.query(models.Location).order_by(desc(models.Location.frequency)).first()
    latest_dream = db.query(models.Dream).order_by(desc(models.Dream.date)).first()
    
    return schemas.WorldStats(
        total_dreams=total_dreams,
        total_locations=total_locations,
        total_entities=total_entities,
        total_transits=total_transits,
        most_frequent_location=most_frequent,
        latest_dream=latest_dream
    )


def export_world(db: Session) -> schemas.WorldExport:
    """Export entire dream world as JSON"""
    dreams = get_dreams(db, limit=10000)
    locations = get_locations(db)
    entities = get_entities(db)
    
    # Get all transits
    transits = db.query(models.Transit).all()
    
    return schemas.WorldExport(
        export_date=datetime.utcnow(),
        dreams=dreams,
        locations=locations,
        entities=entities,
        transits=transits
    )