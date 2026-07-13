"""Basic flight search example for Wayfinder."""

from wayfinder.agent.wayfinder_agent import WayfinderAgent
from wayfinder.models.flight import Flight
from wayfinder.services.flight_service import FlightService
from wayfinder.tools.search_flight_tool import SearchFlightTool


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
    agent = WayfinderAgent(search_flight_tool=search_flight_tool)

    query = "Book me the cheapest flight from Bangalore to Tokyo next Friday."

    print("=========================================")
    print("\u2708\ufe0f  Wayfinder")
    print("Basic Flight Search Example")
    print("=========================================\n")
    print(f"Query: {query}\n")

    result = agent.run(query)

    if isinstance(result, str):
        print(result)
    else:
        print_flights(result)


if __name__ == "__main__":
    main()
