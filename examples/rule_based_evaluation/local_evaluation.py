"""Local rule-based evaluation example for Wayfinder.

Demonstrates how to run a RuleBasedEvaluator against WayfinderAgent results
locally, before integrating with an evaluation platform such as LangSmith.
"""

from rich import print

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
    
    print("[bold]Running rule-based evaluation...[/bold]\n")

    # --- Report ---
    print("[dim]==========================================[/dim]")
    print("[bold blue]✈ Wayfinder[/bold blue]")
    print("[bold]Rule-Based Evaluation[/bold]")
    print("[dim]==========================================[/dim]\n")

    print(f"[cyan]Query[/cyan]             : \"{query}\"")
    print(f"[cyan]Flights Returned[/cyan]  : {len(actual_flights)}\n")

    print_results(evaluation_results)
   
    rule_results = {
        k: v
        for k, v in evaluation_results.items()
        if k != "overall_pass"
    }

    passed = sum(rule_results.values())
    total = len(rule_results)
    overall = evaluation_results["overall_pass"]

    print()
    print("[bold]Evaluation Summary[/bold]")
    print("[dim]------------------------------------------[/dim]")

    if overall:
        print("[bold green]✓ Overall Result : PASS[/bold green]")
    else:
        print("[bold red]✗ Overall Result : FAIL[/bold red]")

    rules_color = "green" if passed == total else "yellow"
    print(f"[bold {rules_color}]Rules Passed     : {passed}/{total}[/bold {rules_color}]")

    print()


if __name__ == "__main__":
    main()
