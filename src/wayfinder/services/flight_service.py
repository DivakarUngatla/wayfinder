"""Flight search service."""

from datetime import datetime, time, timedelta

from wayfinder.models.flight import Flight
from wayfinder.models.flight_search_request import FlightSearchRequest

DEFAULT_CURRENCY = "INR"


class FlightService:
    """
    Provides flight search capabilities for Wayfinder.

    The initial implementation uses an in-memory dataset.
    Future milestones may replace this with a database or
    external airline provider without changing consumers.
    """

    def search_flights(self, request: FlightSearchRequest) -> list[Flight]:
        """Return a predefined set of flights for the requested route."""
        departure_date = request.departure_date

        return [
            Flight(
                airline="ANA",
                flight_number="NH701",
                source=request.source,
                destination=request.destination,
                departure_time=datetime.combine(departure_date, time(6, 30)),
                arrival_time=datetime.combine(departure_date, time(14, 45)),
                duration="8h 15m",
                price=520.00,
                currency=DEFAULT_CURRENCY,
                available_seats=45,
            ),
            Flight(
                airline="Japan Airlines",
                flight_number="JL703",
                source=request.source,
                destination=request.destination,
                departure_time=datetime.combine(departure_date, time(9, 15)),
                arrival_time=datetime.combine(departure_date, time(17, 30)),
                duration="8h 15m",
                price=485.50,
                currency=DEFAULT_CURRENCY,
                available_seats=12,
            ),
            Flight(
                airline="Singapore Airlines",
                flight_number="SQ633",
                source=request.source,
                destination=request.destination,
                departure_time=datetime.combine(departure_date, time(11, 0)),
                arrival_time=datetime.combine(departure_date, time(19, 20)),
                duration="8h 20m",
                price=675.00,
                currency=DEFAULT_CURRENCY,
                available_seats=28,
            ),
            Flight(
                airline="Air India",
                flight_number="AI302",
                source=request.source,
                destination=request.destination,
                departure_time=datetime.combine(departure_date, time(14, 45)),
                arrival_time=datetime.combine(departure_date, time(23, 10)),
                duration="8h 25m",
                price=410.00,
                currency=DEFAULT_CURRENCY,
                available_seats=6,
            ),
            Flight(
                airline="Cathay Pacific",
                flight_number="CX526",
                source=request.source,
                destination=request.destination,
                departure_time=datetime.combine(departure_date, time(18, 30)),
                arrival_time=datetime.combine(
                    departure_date + timedelta(days=1), time(2, 45)
                ),
                duration="8h 15m",
                price=890.00,
                currency=DEFAULT_CURRENCY,
                available_seats=19,
            ),
        ]
