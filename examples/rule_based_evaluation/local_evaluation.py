"""Local rule-based evaluation example for Wayfinder.

Demonstrates how to run a RuleBasedEvaluator against FlightService results
locally, before integrating with an evaluation platform such as LangSmith.
"""

from datetime import timedelta
from datetime import date

from wayfinder.evaluators.rule_based_evaluator import RuleBasedEvaluator
from wayfinder.models.flight_search_request import FlightSearchRequest
from wayfinder.services.flight_service import FlightService


def print_results(results: dict[str, bool]) -> None:
    """Print evaluation results in a human-readable format."""
    for rule, passed in results.items():
        icon = "✓" if passed else "✗"
        print(f"  {icon} {rule}")


def main() -> None:
    """Run a rule-based evaluation on a local flight search."""
    # --- Setup ---
    flight_service = FlightService()
    evaluator = RuleBasedEvaluator()

    # --- Build request ---
    request = FlightSearchRequest(
        source="BLR",
        destination="NRT",
        departure_date=date.today() + timedelta(days=30),
        passengers=1,
    )

    # --- Search ---
    flights = flight_service.search_flights(request)

    # --- Evaluate ---
    results = evaluator.evaluate(request, flights)
    
    print("Running rule-based evaluation...\n")
    # --- Report ---
    print("=========================================")
    print("✈️  Wayfinder")
    print("Rule-Based Evaluation")
    print("=========================================\n")
    print(f"Route      : {request.source} → {request.destination}")
    print(f"Date       : {request.departure_date}")
    print(f"Passengers : {request.passengers}")
    print(f"Flights    : {len(flights)} returned\n")
    print_results(results)
    passed = sum(results.values())
    total = len(results)
    print(f"\nSummary: {passed}/{total} rules passed.")
    print()


if __name__ == "__main__":
    main()
