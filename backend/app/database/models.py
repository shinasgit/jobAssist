from sqlalchemy import Column, Integer, String, DateTime, Text, ForeignKey, UniqueConstraint
from sqlalchemy.orm import relationship
from datetime import datetime, timezone
from .database import Base

class Job(Base):
    __tablename__ = "jobs"

    id = Column(Integer, primary_key=True, index=True)
    title = Column(String, nullable=False)
    company = Column(String, nullable=True)
    location = Column(String, nullable=True)
    remote_type = Column(String, nullable=True)
    salary = Column(String, nullable=True)
    experience = Column(String, nullable=True)
    employment_type = Column(String, nullable=True)
    description = Column(Text, nullable=True)
    source = Column(String, nullable=True)
    source_url = Column(String, nullable=True)
    posted_date = Column(String, nullable=True)
    discovered_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))

    __table_args__ = (
        UniqueConstraint('source', 'source_url', name='uix_source_source_url'),
    )

    saved_entries = relationship("SavedJob", back_populates="job")
    applications = relationship("Application", back_populates="job")

class SavedJob(Base):
    __tablename__ = "saved_jobs"

    id = Column(Integer, primary_key=True, index=True)
    job_id = Column(Integer, ForeignKey("jobs.id"), nullable=False)
    saved_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))
    
    __table_args__ = (
        UniqueConstraint('job_id', name='uix_job_id'),
    )

    job = relationship("Job", back_populates="saved_entries")

class Application(Base):
    __tablename__ = "applications"

    id = Column(Integer, primary_key=True, index=True)
    job_id = Column(Integer, ForeignKey("jobs.id"), nullable=False)
    status = Column(String, nullable=False)
    notes = Column(Text, nullable=True)
    applied_at = Column(DateTime, nullable=True)
    updated_at = Column(DateTime, default=lambda: datetime.now(timezone.utc), onupdate=lambda: datetime.now(timezone.utc))

    job = relationship("Job", back_populates="applications")

class Setting(Base):
    __tablename__ = "settings"

    id = Column(Integer, primary_key=True, index=True)
    keywords = Column(Text, nullable=True)
    locations = Column(Text, nullable=True)
    experience = Column(String, nullable=True)
    remote_type = Column(String, nullable=True)
    employment_types = Column(String, nullable=True)
    enabled_sources = Column(Text, nullable=True)
