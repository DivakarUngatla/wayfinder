"""Basic flight search example for Wayfinder."""

import openai
from dotenv import load_dotenv

from wayfinder.agent.wayfinder_agent import WayfinderAgent
from wayfinder.models.flight import Flight
from wayfinder.services.flight_service import FlightService
from wayfinder.tools.search_flight_tool import SearchFlightTool

load_dotenv()


def print_flights(flights: list[Flight]) -> None:
    """Print a formatted list of flights."""
    print(f"Found {len(flights)} flight(s):\n")
    for flight in flights:
        print(f"  {flight.airline} · {flight.flight_number}")
        print(f"  Route     : {flight.source} → {flight.destination}")
        print(f"  Departure : {flight.departure_time.strftime('%d %b %Y %H:%M')}")
        print(f"  Arrival   : {flight.arrival_time.strftime('%d %b %Y %H:%M')}")
        print(f"  Duration  : {flight.duration}")
        print(f"  Price     : {flight.currency} {flight.price:,.2f}")
        print(f"  Seats     : {flight.available_seats} available")
        print()


def main() -> None:
    """Run a basic flight search."""
    flight_service = FlightService()
    search_flight_tool = SearchFlightTool(flight_service=flight_service)
    agent = WayfinderAgent(search_flight_tool=search_flight_tool, client=openai.OpenAI())

    query = "Book me the cheapest flight from Bangalore to Tokyo next Friday."

    print("=========================================")
    print("✈️  Wayfinder")
    print("Basic Flight Search Example")
    print("=========================================\n")
    print(f"Query: {query}\n")

    result = agent.run(query)

    print("Assistant\n---------")
    print(result.response)
    print()

    if result.flights:
        print("Retrieved Flight Results\n------------------------")
        print_flights(result.flights)


if __name__ == "__main__":
    main()
