"""Flight search result models."""

from datetime import datetime

from pydantic import BaseModel, Field


class Flight(BaseModel):
    """A flight option returned from a flight search."""

    airline: str = Field(description="Name of the operating airline.")
    flight_number: str = Field(description="Airline-assigned flight number.")
    source: str = Field(description="Departure airport or city code.")
    destination: str = Field(description="Arrival airport or city code.")
    departure_time: datetime = Field(description="Scheduled departure date and time.")
    arrival_time: datetime = Field(description="Scheduled arrival date and time.")
    duration: str = Field(
        description="Total flight duration as a human-readable string."
    )
    price: float = Field(description="Ticket price for one passenger.")
    currency: str = Field(description="ISO currency code for the price.")
    available_seats: int = Field(description="Number of seats available for booking.")
