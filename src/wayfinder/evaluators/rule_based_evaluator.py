"""Rule-based evaluator for flight search requests and results."""

from wayfinder.models.flight import Flight
from wayfinder.models.flight_search_request import FlightSearchRequest


class RuleBasedEvaluator:
    """Evaluates flight search requests and results against basic business rules."""

    def evaluate(
        self,
        request: FlightSearchRequest,
        flights: list[Flight],
    ) -> dict[str, bool]:
        """Evaluate a flight search against a set of basic business rules.

        Args:
            request: The incoming flight search request.
            flights: The list of flights returned by the search.

        Returns:
            A dictionary mapping each rule name to a boolean result.
        """
        return {
            "origin_present": bool(request.source and request.source.strip()),
            "destination_present": bool(
                request.destination and request.destination.strip()
            ),
            "flights_returned": bool(flights),
            "prices_available": bool(flights) and all(f.price > 0 for f in flights),
        }
