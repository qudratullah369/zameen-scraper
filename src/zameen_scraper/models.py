from __future__ import annotations

from datetime import datetime, UTC
from typing import Optional

from pydantic import BaseModel, ConfigDict, Field


class PropertyListing(BaseModel):
    """Normalized Zameen.com property listing."""

    model_config = ConfigDict(extra="ignore")

    property_id: Optional[str] = None
    title: Optional[str] = None

    purpose: Optional[str] = None
    property_type: Optional[str] = None

    price: Optional[str] = None
    location: Optional[str] = None
    city: Optional[str] = None
    area: Optional[str] = None
    area_unit: Optional[str] = None

    bedrooms: Optional[int] = None
    bathrooms: Optional[int] = None

    description: Optional[str] = None

    listing_url: Optional[str] = None
    image_urls: list[str] = Field(default_factory=list)

    agent_name: Optional[str] = None
    agency_name: Optional[str] = None

    verified: Optional[bool] = None
    featured: Optional[bool] = None

    listing_status: Optional[str] = None
    date_added: Optional[str] = None
    date_updated: Optional[str] = None

    phone: Optional[str] = None
    whatsapp: Optional[str] = None
    email: Optional[str] = None

    latitude: Optional[float] = None
    longitude: Optional[float] = None

    property_features: list[str] = Field(default_factory=list)

    developer: Optional[str] = None
    project_name: Optional[str] = None

    scraped_at: datetime = Field(default_factory=lambda: datetime.now(UTC))
