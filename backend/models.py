"""
SQLAlchemy ORM models for DreamLand.
Defines database structure for dreams, locations, entities, transits, and changelog.
"""
from sqlalchemy import Column, Integer, String, Float, DateTime, Text, ForeignKey, Enum, Boolean, JSON
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from database import Base
import enum


class LayerEnum(enum.Enum):
    """Dream world layers: lower (-1), primary (0), upper (1)"""
    LOWER = -1
    PRIMARY = 0
    UPPER = 1


class EntityTypeEnum(enum.Enum):
    """Types of entities that can appear in dreams"""
    PERSON = "person"
    BEING = "being"
    ANIMAL = "animal"
    ABSTRACT = "abstract"
    OBJECT = "object"


class ChangeActionEnum(enum.Enum):
    """Actions tracked in changelog"""
    CREATE = "create"
    UPDATE = "update"
    MERGE = "merge"
    SPLIT = "split"
    DELETE = "delete"


class Dream(Base):
    """
    Main dream entry with cycles and content.
    One dream can have multiple cycles (segments).
    """
    __tablename__ = "dreams"

    id = Column(Integer, primary_key=True, index=True)
    date = Column(DateTime, nullable=False, index=True)
    cycle = Column(Integer, default=1)  # Cycle number if multiple in one night
    content = Column(Text, nullable=False)
    language = Column(String(5), default="en")  # ISO language code
    processed = Column(Boolean, default=False)  # AI processing status
    created_at = Column(DateTime, server_default=func.now())
    updated_at = Column(DateTime, server_default=func.now(), onupdate=func.now())

    # Relationships
    locations = relationship("DreamLocation", back_populates="dream", cascade="all, delete-orphan")
    entities = relationship("DreamEntity", back_populates="dream", cascade="all, delete-orphan")
    transits = relationship("Transit", back_populates="dream", cascade="all, delete-orphan")


class Location(Base):
    """
    Master location in the dream world.
    Tracks position, archetype, and appearance frequency.
    """
    __tablename__ = "locations"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(200), nullable=False, index=True)
    archetype = Column(String(100))  # E.g., "home", "forest", "city"
    layer = Column(Enum(LayerEnum), default=LayerEnum.PRIMARY)
    x = Column(Float, default=0.0)  # Normalized -1 to 1
    y = Column(Float, default=0.0)  # Normalized -1 to 1
    symbol = Column(String(50))  # Unicode emoji or symbol
    description = Column(Text)
    color = Column(String(7), default="#3b82f6")  # Hex color for bubble
    frequency = Column(Integer, default=1)  # Number of appearances
    created_at = Column(DateTime, server_default=func.now())
    updated_at = Column(DateTime, server_default=func.now(), onupdate=func.now())

    # Relationships
    dream_locations = relationship("DreamLocation", back_populates="location")
    entities = relationship("Entity", back_populates="location")
    transits_from = relationship("Transit", foreign_keys="Transit.from_location_id", back_populates="from_location")
    transits_to = relationship("Transit", foreign_keys="Transit.to_location_id", back_populates="to_location")


class DreamLocation(Base):
    """
    Many-to-many relationship between dreams and locations.
    Tracks which locations appeared in which dreams.
    """
    __tablename__ = "dream_locations"

    id = Column(Integer, primary_key=True, index=True)
    dream_id = Column(Integer, ForeignKey("dreams.id", ondelete="CASCADE"), nullable=False)
    location_id = Column(Integer, ForeignKey("locations.id", ondelete="CASCADE"), nullable=False)
    order = Column(Integer, default=0)  # Order of appearance in dream

    # Relationships
    dream = relationship("Dream", back_populates="locations")
    location = relationship("Location", back_populates="dream_locations")


class Entity(Base):
    """
    Master entity (person, being, animal, object, abstract concept).
    Can be associated with locations or appear independently.
    """
    __tablename__ = "entities"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(200), nullable=False, index=True)
    type = Column(Enum(EntityTypeEnum), nullable=False)
    description = Column(Text)
    symbol = Column(String(50))  # Unicode emoji or symbol
    confidence = Column(Float, default=1.0)  # AI extraction confidence 0-1
    location_id = Column(Integer, ForeignKey("locations.id", ondelete="SET NULL"), nullable=True)
    created_at = Column(DateTime, server_default=func.now())

    # Relationships
    location = relationship("Location", back_populates="entities")
    dream_entities = relationship("DreamEntity", back_populates="entity")


class DreamEntity(Base):
    """
    Many-to-many relationship between dreams and entities.
    Tracks which entities appeared in which dreams.
    """
    __tablename__ = "dream_entities"

    id = Column(Integer, primary_key=True, index=True)
    dream_id = Column(Integer, ForeignKey("dreams.id", ondelete="CASCADE"), nullable=False)
    entity_id = Column(Integer, ForeignKey("entities.id", ondelete="CASCADE"), nullable=False)

    # Relationships
    dream = relationship("Dream", back_populates="entities")
    entity = relationship("Entity", back_populates="dream_entities")


class Transit(Base):
    """
    Movement between locations with trigger/cause.
    Represents how dreamer moved from one place to another.
    """
    __tablename__ = "transits"

    id = Column(Integer, primary_key=True, index=True)
    dream_id = Column(Integer, ForeignKey("dreams.id", ondelete="CASCADE"), nullable=False)
    from_location_id = Column(Integer, ForeignKey("locations.id", ondelete="CASCADE"), nullable=False)
    to_location_id = Column(Integer, ForeignKey("locations.id", ondelete="CASCADE"), nullable=False)
    trigger = Column(Text)  # What caused the transition
    confidence = Column(Float, default=1.0)  # AI extraction confidence 0-1
    created_at = Column(DateTime, server_default=func.now())

    # Relationships
    dream = relationship("Dream", back_populates="transits")
    from_location = relationship("Location", foreign_keys=[from_location_id], back_populates="transits_from")
    to_location = relationship("Location", foreign_keys=[to_location_id], back_populates="transits_to")


class ChangeLog(Base):
    """
    Version control for manual edits and AI suggestions.
    Tracks all changes to locations including merges and splits.
    """
    __tablename__ = "changelog"

    id = Column(Integer, primary_key=True, index=True)
    action = Column(Enum(ChangeActionEnum), nullable=False)
    entity_type = Column(String(50), nullable=False)  # "location", "entity", etc.
    entity_id = Column(Integer, nullable=False)  # ID of affected entity
    old_data = Column(JSON)  # Snapshot before change
    new_data = Column(JSON)  # Snapshot after change
    merged_from = Column(JSON)  # List of IDs if merge action
    split_into = Column(JSON)  # List of IDs if split action
    user_note = Column(Text)  # Optional user comment
    timestamp = Column(DateTime, server_default=func.now())