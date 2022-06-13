from datetime import datetime

from sqlalchemy import Column, Integer, String, Float, DATETIME, Boolean

from . import Base


class Source(Base):
    __tablename__ = "sources"

    id = Column(Integer, primary_key=True, unique=True, nullable=False, autoincrement=True)
    url = Column(String, unique=True, nullable=False)
    score = Column(Float)
    traffic = Column(Float)
    blacklisted = Column(Boolean)
    org = Column(String)
    government = Column(Boolean)
    created_at = Column(DATETIME)
    cert_expires_at = Column(DATETIME)
    ipv4 = Column(String)
    ipv6 = Column(String)
    date_added = Column(DATETIME, default=datetime.now)
    date_updated = Column(DATETIME, default=datetime.now)


class Document(Base):
    __tablename__ = "documents"

    id = Column(Integer, primary_key=True, unique=True, nullable=False, autoincrement=True)
    url = Column(String)
    title = Column(String)
    text = Column(String)
    s_id = Column(Integer)
    ar_id = Column(Integer)
    entity_uuid = Column(String)
    created_at = Column(DATETIME)
    date_added = Column(DATETIME, default=datetime.now)
    date_updated = Column(DATETIME, default=datetime.now)


class AnalysisResult(Base):
    __tablename__ = "analysis_results"

    id = Column(Integer, primary_key=True, unique=True, nullable=False, autoincrement=True)
    # Block 1
    primary_source_url = Column(String)
    created_at = Column(DATETIME)
    text = Column(String)
    source_score = Column(Float)
    times_published = Column(Integer)
    percentage_blacklist = Column(Float)
    source_text = Column(String)
    avg_sources_score = Column(Float)
    reliable_sources_flag = Column(Boolean)
    # Block 2
    diagram_data = Column(String)
    # Block 3
    plagiary_percentage = Column(Float)
    is_any_sentiment_delta = Column(Float)
    facts = Column(String)
    # Block 4
    grammatic_errors_count = Column(Integer)
    spam_index = Column(Float)
    water_index = Column(Float)
    sentiment_index = Column(Float)
    speech_index = Column(Float)
    intuition_index = Column(Float)
    clickbait_index = Column(Float)
    rationality_index = Column(Float)
    fake_index = Column(Float)

    date_added = Column(DATETIME, default=datetime.now)
    date_updated = Column(DATETIME, default=datetime.now)


class BlacklistedSource(Base):
    __tablename__ = "blacklisted_sources"

    id = Column(Integer, primary_key=True, unique=True, nullable=False, autoincrement=True)
    ipv4 = Column(String)
    ipv6 = Column(String)
    url = Column(String, unique=True, nullable=False)
    date_added = Column(DATETIME, default=datetime.now)
    date_updated = Column(DATETIME, default=datetime.now)