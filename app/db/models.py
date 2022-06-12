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
    date_added = Column(DATETIME, default=datetime.now)
    date_updated = Column(DATETIME, default=datetime.now)
    is_primary_source = Column(Boolean)
    date_delta = Column(Integer)
    difference = Column(Float)
    difference_sum = Column(Float)
    delta_tone_vector = Column(Float)
    crossed_words = Column(String)
    diagram_1 = Column(String)
    is_real_publication_date = Column(Boolean)
    is_publication_date_difference = Column(Boolean)
    is_author_shown = Column(Boolean)
    real_references = Column(String)
    is_organisation_real = Column(Boolean)
    author_rate = Column(Float)
    mistakes_count = Column(Integer)
    spam_index = Column(Float)
    water_index = Column(Float)
    is_directional_pronouns_used = Column(Boolean)
    is_direct_appear = Column(Boolean)
    is_any_links = Column(Boolean)


class BlacklistedSource(Base):
    __tablename__ = "blacklisted_sources"

    id = Column(Integer, primary_key=True, unique=True, nullable=False, autoincrement=True)
    ipv4 = Column(String)
    ipv6 = Column(String)
    url = Column(String, unique=True, nullable=False)
    date_added = Column(DATETIME, default=datetime.now)
    date_updated = Column(DATETIME, default=datetime.now)