from typing import List, Union
from datetime import datetime
from urllib.parse import urlparse

from pydantic import BaseModel, AnyUrl, validator


class PyNewDocument(BaseModel):
    url: Union[AnyUrl, None]
    title: Union[str, None]
    text: Union[str, None]

    @validator("title", "text", always=True)
    def mutually_exclusive(cls, v, values):
        if values.get("url") is not None and v:
            raise ValueError("'url' and ('title', 'text') are mutually exclusive")
        return v


class PyDocument(BaseModel):
    id: int
    url: Union[str, None]
    title: Union[str, None]
    text: Union[str, None]
    s_id: Union[int, None]
    ar_id: Union[int, None]
    entity_uuid: Union[str, None]
    created_at: Union[datetime, None]
    date_added: datetime
    date_updated: datetime

    class Config:
        orm_mode = True


class PyNewSource(BaseModel):
    url: AnyUrl
    score: Union[float, None]

    @validator("url")
    def is_absolute(cls, v):
        if not bool(urlparse(v).netloc):
            raise ValueError("'url' must be absolute")
        return v


class PySource(BaseModel):
    id: int
    url: Union[str, None]
    score: Union[float, None]
    date_added: datetime
    date_updated: datetime


class PySourcesAnalysisResult(BaseModel):
    sources: List[PySource]
    good_media_percentage: Union[float, None]
    media_avg_score: Union[float, None]


class PyAnalysisResult(BaseModel):
    id: int
    date_added: datetime
    date_updated: datetime
    is_primary_source: Union[bool, None]
    date_delta: Union[int, None]
    difference: Union[float, None]
    difference_sum: Union[float, None]
    delta_tone_vector: Union[float, None]
    crossed_words: Union[str, None]
    diagram_1: Union[str, None]
    is_real_publication_date: Union[bool, None]
    is_publication_date_difference: Union[bool, None]
    is_author_shown: Union[bool, None]
    real_references: Union[str, None]
    is_organisation_real: Union[bool, None]
    author_rate: Union[float, None]
    mistakes_count: Union[int, None]
    spam_index: Union[float, None]
    water_index: Union[float, None]
    is_directional_pronouns_used: Union[bool, None]
    is_direct_appear: Union[bool, None]
    is_any_links: Union[bool, None]

    class Config:
        orm_mode = True
