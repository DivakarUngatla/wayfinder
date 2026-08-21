"""Flight search request models."""

from datetime import date

from pydantic import BaseModel, Field


class FlightSearchRequest(BaseModel):
    """A user's request to search for available flights.

    Also carries the result of inline intent classification: if the user's
    request is not a supported flight search, is_flight_search is False and
    rejection_response contains the text to return to the user.
    """

    is_flight_search: bool = Field(
        default=True,
        description=(
            "True if the user's primary intent is to search for or compare "
            "available flights. False if the request involves anything "
            "Wayfinder cannot do (booking, payment, cancellation, weather, "
            "visa, hotels, etc.)."
        ),
    )
    rejection_response: str | None = Field(
        default=None,
        description=(
            "When is_flight_search is False: a polite, concise explanation "
            "that acknowledges the request, says it is outside Wayfinder's "
            "capabilities, and mentions what Wayfinder can help with. "
            "Must be null when is_flight_search is True."
        ),
    )
    source: str = Field(description="Departure airport or city code. Empty string if not provided by the user.")
    destination: str = Field(description="Arrival airport or city code. Empty string if not provided by the user.")
    departure_date: date = Field(description="Requested departure date.")
    passengers: int = Field(default=1, description="Number of passengers to book.")
