import pytest
from datetime import date, time

from wayfinder.models.flight_search_request import FlightSearchRequest
from wayfinder.services.flight_service import FlightService


@pytest.fixture
def service():
    return FlightService()


def test_flight_service_available_seats(service):
    """Test filtering by available seats."""
    req = FlightSearchRequest(
        source="Bangalore",
        destination="Tokyo",
        departure_date=date(2026, 9, 4),
        passengers=20,
    )
    flights = service.search_flights(req)
    
    assert len(flights) == 2
    for flight in flights:
        assert flight.available_seats >= 20


def test_flight_service_price_sorting(service):
    """Test sorting by price ascending."""
    req = FlightSearchRequest(
        source="Bangalore",
        destination="Tokyo",
        departure_date=date(2026, 9, 4),
        sort_by="price"
    )
    flights = service.search_flights(req)
    
    assert len(flights) == 5
    assert flights[0].price == 41000.00
    assert flights[1].price == 48550.00
    assert flights[-1].price == 89000.00


def test_flight_service_duration_sorting(service):
    """Test sorting by duration ascending."""
    req = FlightSearchRequest(
        source="Bangalore",
        destination="Tokyo",
        departure_date=date(2026, 9, 4),
        sort_by="duration"
    )
    flights = service.search_flights(req)
    
    assert len(flights) == 5
    assert flights[0].duration == "8h 15m"


def test_flight_service_arrival_before_filtering_and_timezone(service):
    """Test filtering by arrival before, handling timezone awareness."""
    from datetime import timezone, timedelta
    tz_aware_time = time(20, 0, tzinfo=timezone(timedelta(hours=5, minutes=30)))
    
    req = FlightSearchRequest(
        source="Bangalore",
        destination="Tokyo",
        departure_date=date(2026, 9, 4),
        arrival_before=tz_aware_time
    )
    flights = service.search_flights(req)
    
    assert len(flights) == 3
    for flight in flights:
        assert flight.arrival_time.time() < time(20, 0)
