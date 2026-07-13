"""Flight search request models."""

from datetime import date

from pydantic import BaseModel, Field


class FlightSearchRequest(BaseModel):
    """A user's request to search for available flights."""

    source: str = Field(description="Departure airport or city code.")
    destination: str = Field(description="Arrival airport or city code.")
    departure_date: date = Field(description="Requested departure date.")
    passengers: int = Field(default=1, description="Number of passengers to book.")
