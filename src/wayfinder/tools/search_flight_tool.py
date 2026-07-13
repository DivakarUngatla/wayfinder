"""Flight search tool."""

from wayfinder.models.flight import Flight
from wayfinder.models.flight_search_request import FlightSearchRequest
from wayfinder.services.flight_service import FlightService


class SearchFlightTool:
    """Tool that delegates flight search requests to FlightService."""

    def __init__(self, flight_service: FlightService) -> None:
        """Initialize the tool with a flight service instance."""
        self._flight_service = flight_service

    def search(self, request: FlightSearchRequest) -> list[Flight]:
        """Search for flights matching the given request."""
        return self._flight_service.search_flights(request)
