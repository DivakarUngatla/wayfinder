"""Wayfinder agent."""

from datetime import date

from wayfinder.models.flight import Flight
from wayfinder.models.flight_search_request import FlightSearchRequest
from wayfinder.tools.search_flight_tool import SearchFlightTool


class WayfinderAgent:
    """Orchestrates flight search without using an LLM."""

    def __init__(self, search_flight_tool: SearchFlightTool) -> None:
        """Initialize the agent with a flight search tool."""
        self._search_flight_tool = search_flight_tool

    def run(self, user_query: str) -> list[Flight] | str:
        """Process a user query and return matching flights.

        This example intentionally uses simple rule-based parsing to keep the
        focus on evaluation concepts. Later parts of the series replace this
        logic with a more capable AI-powered agent.
        """
        query = user_query.lower()

        if "bangalore" in query and "tokyo" in query:
            request = FlightSearchRequest(
                source="Bangalore",
                destination="Tokyo",
                departure_date=date.today(),
                passengers=1,
            )
                    
            return self._search_flight_tool.search(request)

        return "Unsupported request."