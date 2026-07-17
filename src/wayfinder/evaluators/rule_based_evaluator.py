"""Rule-based evaluator for flight search results."""

from wayfinder.models.flight import Flight


class RuleBasedEvaluator:
    """Evaluates flight search results against deterministic business rules."""

    def evaluate(
        self, ground_truth_flights: list[Flight], actual_flights: list[Flight]
    ) -> dict[str, bool]:
        """Evaluate a list of actual flights against ground truth flights.

        Args:
            ground_truth_flights: The ground truth flights from the dataset.
            actual_flights: The list of actual flights returned by the agent.

        Returns:
            A dictionary mapping each rule name to a boolean result.
        """
        expected_source = ground_truth_flights[0].source.strip().lower() if ground_truth_flights else ""
        expected_dest = ground_truth_flights[0].destination.strip().lower() if ground_truth_flights else ""

        rules = {
            "flights_returned": bool(actual_flights),
            "all_flights_match_ground_truth_source": bool(actual_flights)
            and all(f.source.strip().lower() == expected_source for f in actual_flights),
            "all_flights_match_ground_truth_destination": bool(actual_flights)
            and all(f.destination.strip().lower() == expected_dest for f in actual_flights),
            "all_flights_have_positive_price": bool(actual_flights)
            and all(f.price > 0 for f in actual_flights),
            "all_flights_have_flight_number": bool(actual_flights)
            and all(bool(f.flight_number.strip()) for f in actual_flights),
        }

        # Compute overall_pass and make it the first key
        results = {"overall_pass": all(rules.values())}
        results.update(rules)
        return results
