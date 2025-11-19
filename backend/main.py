"""
FastAPI main application.
Defines all API endpoints for DreamLand MVP.
"""
from fastapi import FastAPI, Depends, HTTPException, BackgroundTasks
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session
from typing import List, Optional
import os
from dotenv import load_dotenv

import models
import schemas
import crud
import tasks
from database import get_db, init_db

load_dotenv()

# Initialize FastAPI app
app = FastAPI(
    title="DreamLand API",
    description="API for dream journaling and world mapping",
    version="1.0.0"
)

# CORS configuration
allowed_origins = os.getenv("ALLOWED_ORIGINS", "http://localhost:5173").split(",")
app.add_middleware(
    CORSMiddleware,
    allow_origins=allowed_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.on_event("startup")
def startup_event():
    """Initialize database on startup"""
    init_db()
    print("✅ Database initialized")


@app.get("/")
def read_root():
    """Health check endpoint"""
    return {"status": "ok", "message": "DreamLand API is running"}


# Dream endpoints
@app.post("/api/dreams", response_model=schemas.DreamResponse, status_code=201)
async def create_dream(
    dream: schemas.DreamCreate,
    background_tasks: BackgroundTasks,
    db: Session = Depends(get_db)
):
    """
    Create a new dream entry.
    Triggers async processing for AI extraction.
    """
    db_dream = crud.create_dream(db, dream)
    
    # Schedule background processing
    background_tasks.add_task(tasks.process_dream_async, db_dream.id, db)
    
    return db_dream


@app.get("/api/dreams", response_model=List[schemas.DreamResponse])
def get_dreams(
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db)
):
    """Get all dreams with pagination"""
    return crud.get_dreams(db, skip=skip, limit=limit)


@app.get("/api/dreams/{dream_id}", response_model=schemas.DreamResponse)
def get_dream(dream_id: int, db: Session = Depends(get_db)):
    """Get a specific dream by ID"""
    dream = crud.get_dream(db, dream_id)
    if not dream:
        raise HTTPException(status_code=404, detail="Dream not found")
    return dream


# Location endpoints
@app.get("/api/locations", response_model=List[schemas.LocationResponse])
def get_locations(
    layer: Optional[str] = None,
    db: Session = Depends(get_db)
):
    """
    Get all locations, optionally filtered by layer.
    Layer can be: PRIMARY, UPPER, LOWER
    """
    layer_enum = None
    if layer:
        try:
            layer_enum = models.LayerEnum[layer.upper()]
        except KeyError:
            raise HTTPException(status_code=400, detail="Invalid layer value")
    
    return crud.get_locations(db, layer=layer_enum)


@app.get("/api/locations/{location_id}", response_model=schemas.LocationResponse)
def get_location(location_id: int, db: Session = Depends(get_db)):
    """Get a specific location by ID"""
    location = crud.get_location(db, location_id)
    if not location:
        raise HTTPException(status_code=404, detail="Location not found")
    return location


@app.post("/api/locations", response_model=schemas.LocationResponse, status_code=201)
def create_location(
    location: schemas.LocationCreate,
    db: Session = Depends(get_db)
):
    """Create a new location manually"""
    return crud.create_location(db, location)


@app.patch("/api/locations/{location_id}", response_model=schemas.LocationResponse)
def update_location(
    location_id: int,
    location_update: schemas.LocationUpdate,
    db: Session = Depends(get_db)
):
    """Update a location (position, name, etc.)"""
    updated = crud.update_location(db, location_id, location_update)
    if not updated:
        raise HTTPException(status_code=404, detail="Location not found")
    return updated


@app.post("/api/locations/merge", response_model=schemas.LocationResponse)
def merge_locations(
    merge_request: schemas.LocationMergeRequest,
    db: Session = Depends(get_db)
):
    """Merge multiple locations into one"""
    try:
        merged = crud.merge_locations(
            db,
            source_ids=merge_request.source_ids,
            target_name=merge_request.target_name,
            user_note=merge_request.user_note
        )
        return merged
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


# Entity endpoints
@app.get("/api/entities", response_model=List[schemas.EntityResponse])
def get_entities(
    location_id: Optional[int] = None,
    db: Session = Depends(get_db)
):
    """Get all entities, optionally filtered by location"""
    return crud.get_entities(db, location_id=location_id)


@app.get("/api/entities/{entity_id}", response_model=schemas.EntityResponse)
def get_entity(entity_id: int, db: Session = Depends(get_db)):
    """Get a specific entity by ID"""
    entity = crud.get_entity(db, entity_id)
    if not entity:
        raise HTTPException(status_code=404, detail="Entity not found")
    return entity


@app.post("/api/entities", response_model=schemas.EntityResponse, status_code=201)
def create_entity(
    entity: schemas.EntityCreate,
    db: Session = Depends(get_db)
):
    """Create a new entity manually"""
    return crud.create_entity(db, entity)


# Transit endpoints
@app.get("/api/locations/{location_id}/transits", response_model=List[schemas.TransitResponse])
def get_location_transits(location_id: int, db: Session = Depends(get_db)):
    """Get all transits from or to a specific location"""
    return crud.get_transits_for_location(db, location_id)


# Stats and export endpoints
@app.get("/api/stats", response_model=schemas.WorldStats)
def get_stats(db: Session = Depends(get_db)):
    """Get statistics about the dream world"""
    return crud.get_world_stats(db)


@app.get("/api/export", response_model=schemas.WorldExport)
def export_world(db: Session = Depends(get_db)):
    """Export entire dream world as JSON"""
    return crud.export_world(db)


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)