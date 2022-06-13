from typing import List, Union
from datetime import datetime
from urllib.parse import urlparse
from ipaddress import IPv4Address, IPv6Address

from pydantic import BaseModel, AnyUrl, validator


class NewPyDocument(BaseModel):
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


class NewPySource(BaseModel):
    url: AnyUrl
    score: Union[float, None]
    ipv4: Union[IPv4Address, None]
    ipv6: Union[IPv6Address, None]

    @validator("url")
    def is_absolute(cls, v):
        if not bool(urlparse(v).netloc):
            raise ValueError("'url' must be absolute")
        return v


class PySource(BaseModel):
    id: int
    url: str
    score: Union[float, None]
    traffic: Union[float, None]
    blacklisted: Union[bool, None]
    org: Union[str, None]
    government: Union[bool, None]
    created_at: datetime
    cert_expires_at: Union[datetime, None]
    ipv4: Union[IPv4Address, None]
    ipv6: Union[IPv6Address, None]
    date_added: datetime
    date_updated: datetime

    class Config:
        orm_mode = True


class PySourcesAnalysisResult(BaseModel):
    sources: List[PySource]
    good_media_percentage: Union[float, None]
    media_avg_score: Union[float, None]

    class Config:
        orm_mode = True


class DiagramData(BaseModel):
    date: Union[str, None]
    is_valid: Union[bool, None]


class DiagramData(BaseModel):
    date: Union[str, None]
    is_valid: Union[bool, None]


class PyAnalysisResult(BaseModel):
    id: int
    # Block 1
    primary_source_url: Union[str, None]
    created_at: Union[datetime, None]
    text: Union[str, None]
    source_score: Union[float, None]
    times_published: Union[int, None]
    percentage_blacklist: Union[float, None]
    source_text: Union[str, None]
    avg_sources_score: Union[float, None]
    reliable_sources_flag: Union[bool, None]
    # Bloack 2
    diagram_data: Union[str, None]
    #
    plagiary_percentage: Union[str, None]
    is_any_sentiment_delta: Union[bool, None]
    facts: Union[str, None]
    #
    grammatic_errors_count: Union[int, None]
    spam_index: Union[float, None]
    water_index: Union[float, None]
    sentiment_index: Union[float, None]
    speech_index: Union[float, None]
    intuition_index: Union[float, None]
    clickbait_index: Union[float, None]
    rationality_index: Union[float, None]
    fake_index: Union[float, None]
    date_added: datetime
    date_updated: datetime

    class Config:
        orm_mode = True


class NewPyBlacklistedSource(BaseModel):
    ipv4: IPv4Address
    ipv6: IPv6Address
    url: AnyUrl

    @validator("ipv4", "ipv6", "url", always=True)
    def any_of(cls, v, values):
        if len(values) == 3 and not any([value for _, value in values.items()]):
            raise ValueError("at least one of 'ipv4', 'ipv6', 'url' must be provided")
        return v


class PyBlacklistedSource(BaseModel):
    ipv4: IPv4Address
    ipv6: IPv6Address
    url: AnyUrl

    @validator("ipv4", "ipv6", "url", always=True)
    def any_of(cls, v, values):
        if len(values) == 3 and not any([value for _, value in values.items()]):
            raise ValueError("at least one of 'ipv4', 'ipv6', 'url' must be provided")
        return v

    class Config:
        orm_mode = True