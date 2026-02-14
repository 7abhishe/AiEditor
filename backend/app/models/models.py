"""
CodeGenie AI Editor — SQLAlchemy Database Models
Matches the ER diagram from architect.md
"""

import uuid
from datetime import datetime, timezone

from sqlalchemy import Boolean, Column, DateTime, ForeignKey, String, Text, JSON
from sqlalchemy.dialects.postgresql import UUID as PG_UUID
from sqlalchemy.orm import relationship

from app.core.database import Base


def generate_uuid():
    return str(uuid.uuid4())


def utc_now():
    return datetime.now(timezone.utc)


class APIKey(Base):
    """API Key for authenticating requests."""

    __tablename__ = "api_keys"

    id = Column(String(36), primary_key=True, default=generate_uuid)
    key_hash = Column(String(128), unique=True, nullable=False, index=True)
    label = Column(String(100), nullable=False, default="default")
    permissions = Column(String(50), nullable=False, default="read,write")
    is_active = Column(Boolean, default=True, nullable=False)
    created_at = Column(DateTime(timezone=True), default=utc_now, nullable=False)
    last_used_at = Column(DateTime(timezone=True), nullable=True)
    expires_at = Column(DateTime(timezone=True), nullable=True)

    # Relationships
    projects = relationship("Project", back_populates="api_key", cascade="all, delete-orphan")
    conversations = relationship("Conversation", back_populates="api_key", cascade="all, delete-orphan")

    def __repr__(self):
        return f"<APIKey label={self.label} active={self.is_active}>"


class Project(Base):
    """A project (repository) opened in CodeGenie."""

    __tablename__ = "projects"

    id = Column(String(36), primary_key=True, default=generate_uuid)
    api_key_id = Column(String(36), ForeignKey("api_keys.id"), nullable=False)
    name = Column(String(255), nullable=False)
    root_path = Column(Text, nullable=False)
    last_indexed = Column(DateTime(timezone=True), nullable=True)
    created_at = Column(DateTime(timezone=True), default=utc_now, nullable=False)

    # Relationships
    api_key = relationship("APIKey", back_populates="projects")
    conversations = relationship("Conversation", back_populates="project", cascade="all, delete-orphan")

    def __repr__(self):
        return f"<Project name={self.name}>"


class Conversation(Base):
    """A chat conversation session."""

    __tablename__ = "conversations"

    id = Column(String(36), primary_key=True, default=generate_uuid)
    api_key_id = Column(String(36), ForeignKey("api_keys.id"), nullable=False)
    project_id = Column(String(36), ForeignKey("projects.id"), nullable=True)
    title = Column(String(255), nullable=False, default="New Conversation")
    created_at = Column(DateTime(timezone=True), default=utc_now, nullable=False)

    # Relationships
    api_key = relationship("APIKey", back_populates="conversations")
    project = relationship("Project", back_populates="conversations")
    messages = relationship("Message", back_populates="conversation", cascade="all, delete-orphan")

    def __repr__(self):
        return f"<Conversation title={self.title}>"


class Message(Base):
    """A single message in a conversation."""

    __tablename__ = "messages"

    id = Column(String(36), primary_key=True, default=generate_uuid)
    conversation_id = Column(String(36), ForeignKey("conversations.id"), nullable=False)
    role = Column(String(20), nullable=False)  # 'user', 'assistant', 'system'
    content = Column(Text, nullable=False)
    metadata_ = Column("metadata", JSON, nullable=True)
    created_at = Column(DateTime(timezone=True), default=utc_now, nullable=False)

    # Relationships
    conversation = relationship("Conversation", back_populates="messages")

    def __repr__(self):
        return f"<Message role={self.role} conversation={self.conversation_id}>"
