"""
Pydantic schemas for request/response validation.
Defines data structures for API endpoints.
"""
from pydantic import BaseModel, Field, validator
from datetime import datetime
from typing import Optional, List
from models import LayerEnum, EntityTypeEnum, ChangeActionEnum


# Dream Schemas
class DreamCreate(BaseModel):
    """Request schema for creating a new dream"""
    date: datetime
    cycle: int = Field(default=1, ge=1)
    content: str = Field(min_length=1)
    language: str = Field(default="en", max_length=5)


class DreamResponse(BaseModel):
    """Response schema for dream data"""
    id: int
    date: datetime
    cycle: int
    content: str
    language: str
    processed: bool
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


# Location Schemas
class LocationCreate(BaseModel):
    """Request schema for creating a location"""
    name: str = Field(min_length=1, max_length=200)
    archetype: Optional[str] = None
    layer: LayerEnum = LayerEnum.PRIMARY
    x: float = Field(default=0.0, ge=-1.0, le=1.0)
    y: float = Field(default=0.0, ge=-1.0, le=1.0)
    symbol: Optional[str] = None
    description: Optional[str] = None
    color: str = Field(default="#3b82f6", pattern="^#[0-9A-Fa-f]{6}$")


class LocationUpdate(BaseModel):
    """Request schema for updating a location"""
    name: Optional[str] = None
    archetype: Optional[str] = None
    layer: Optional[LayerEnum] = None
    x: Optional[float] = Field(None, ge=-1.0, le=1.0)
    y: Optional[float] = Field(None, ge=-1.0, le=1.0)
    symbol: Optional[str] = None
    description: Optional[str] = None
    color: Optional[str] = Field(None, pattern="^#[0-9A-Fa-f]{6}$")


class LocationResponse(BaseModel):
    """Response schema for location data"""
    id: int
    name: str
    archetype: Optional[str]
    layer: str
    x: float
    y: float
    symbol: Optional[str]
    description: Optional[str]
    color: str
    frequency: int
    created_at: datetime
    updated_at: datetime

    @validator('layer', pre=True)
    def convert_layer(cls, v):
        if isinstance(v, LayerEnum):
            return v.name
        return v

    class Config:
        from_attributes = True


# Entity Schemas
class EntityCreate(BaseModel):
    """Request schema for creating an entity"""
    name: str = Field(min_length=1, max_length=200)
    type: EntityTypeEnum
    description: Optional[str] = None
    symbol: Optional[str] = None
    confidence: float = Field(default=1.0, ge=0.0, le=1.0)
    location_id: Optional[int] = None


class EntityResponse(BaseModel):
    """Response schema for entity data"""
    id: int
    name: str
    type: str
    description: Optional[str]
    symbol: Optional[str]
    confidence: float
    location_id: Optional[int]
    created_at: datetime

    @validator('type', pre=True)
    def convert_type(cls, v):
        if isinstance(v, EntityTypeEnum):
            return v.value
        return v

    class Config:
        from_attributes = True


# Transit Schemas
class TransitCreate(BaseModel):
    """Request schema for creating a transit"""
    from_location_id: int
    to_location_id: int
    trigger: Optional[str] = None
    confidence: float = Field(default=1.0, ge=0.0, le=1.0)


class TransitResponse(BaseModel):
    """Response schema for transit data"""
    id: int
    from_location_id: int
    to_location_id: int
    trigger: Optional[str]
    confidence: float
    created_at: datetime

    class Config:
        from_attributes = True


# AI Extraction Results
class AIExtractionResult(BaseModel):
    """Schema for AI extraction results from dream content"""
    locations: List[LocationCreate]
    entities: List[EntityCreate]
    transits: List[TransitCreate]


# Merge/Split Schemas
class LocationMergeRequest(BaseModel):
    """Request schema for merging locations"""
    source_ids: List[int] = Field(min_items=2)
    target_name: str
    user_note: Optional[str] = None


class LocationSplitRequest(BaseModel):
    """Request schema for splitting a location"""
    source_id: int
    new_locations: List[LocationCreate] = Field(min_items=2)
    user_note: Optional[str] = None


# Export Schema
class WorldExport(BaseModel):
    """Schema for exporting entire dream world as JSON"""
    export_date: datetime
    dreams: List[DreamResponse]
    locations: List[LocationResponse]
    entities: List[EntityResponse]
    transits: List[TransitResponse]


# Stats Schema
class WorldStats(BaseModel):
    """Statistics about the dream world"""
    total_dreams: int
    total_locations: int
    total_entities: int
    total_transits: int
    most_frequent_location: Optional[LocationResponse]

    latest_dream: Optional[DreamResponse]
