"""Local rule-based evaluation example for Wayfinder.

Demonstrates how to run a RuleBasedEvaluator against WayfinderAgent results
locally, before integrating with an evaluation platform such as LangSmith.
"""

from wayfinder.agent.wayfinder_agent import WayfinderAgent
from wayfinder.evaluators.rule_based_evaluator import RuleBasedEvaluator
from wayfinder.models.flight import Flight
from wayfinder.services.flight_service import FlightService
from wayfinder.tools.search_flight_tool import SearchFlightTool


def print_results(results: dict[str, bool]) -> None:
    """Print evaluation results in a human-readable format."""
    for rule, passed in results.items():
        icon = "✓" if passed else "✗"
        print(f"  {icon} {rule}")


def main() -> None:
    """Run a rule-based evaluation on a local flight search."""
    # --- Setup ---
    flight_service = FlightService()
    search_flight_tool = SearchFlightTool(flight_service=flight_service)
    agent = WayfinderAgent(search_flight_tool=search_flight_tool)
    evaluator = RuleBasedEvaluator()

    # --- Search ---
    query = "Book me a flight from Bangalore to Tokyo"
    result = agent.run(query)
    actual_flights = result if isinstance(result, list) else []

    # --- Evaluate ---
    ground_truth_flights = [
        # The ground truth intentionally contains only the fields relevant to this
        # evaluation. We bypass validation because Flight is our production model
        # with additional required fields.
        Flight.model_construct(
            source="Bangalore",
            destination="Tokyo"

        )
    ]
    evaluation_results = evaluator.evaluate(ground_truth_flights, actual_flights)
    
    print("Running rule-based evaluation...\n")
    # --- Report ---
    print("=========================================")
    print("✈️  Wayfinder")
    print("Rule-Based Evaluation")
    print("=========================================\n")
    print(f"Query      : \"{query}\"")
    print(f"Flights Returned : {len(actual_flights)}\n")
    print_results(evaluation_results)
    passed = sum(evaluation_results.values())
    total = len(evaluation_results)
    print(f"\nSummary: {passed}/{total} rules passed.")
    print()


if __name__ == "__main__":
    main()
