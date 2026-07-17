"""LangSmith evaluation example for Wayfinder.

Demonstrates how to execute the existing RuleBasedEvaluator using LangSmith,
evaluating WayfinderAgent as the public entry point.
"""

from typing import Any

from dotenv import load_dotenv
from langsmith import Client, evaluate

from wayfinder.agent.wayfinder_agent import WayfinderAgent
from wayfinder.evaluators.rule_based_evaluator import RuleBasedEvaluator
from wayfinder.models.flight import Flight
from wayfinder.services.flight_service import FlightService
from wayfinder.tools.search_flight_tool import SearchFlightTool

# Load environment variables from .env
load_dotenv()

# --- Shared instances (constructor injection) ---
flight_service = FlightService()
search_flight_tool = SearchFlightTool(flight_service=flight_service)
agent = WayfinderAgent(search_flight_tool=search_flight_tool)
evaluator = RuleBasedEvaluator()


def target(inputs: dict) -> dict:
    """Invoke the agent with a user query and return the results."""
    result = agent.run(inputs["query"])
    flights = result if isinstance(result, list) else []
    # Convert Flight models into JSON-serializable dictionaries for LangSmith.
    return {"flights": [f.model_dump(mode="json") for f in flights]}


# Adapter that compares the application's predicted output against
# the dataset's ground truth output and converts the evaluation
# results into LangSmith's expected format.
def langsmith_rule_based_evaluator(
    inputs: dict, outputs: dict, reference_outputs: dict | None = None
) -> dict[str, Any]:
    """Adapt RuleBasedEvaluator output to the LangSmith evaluator format."""
    ground_truth_outputs = reference_outputs or {}
    
    ground_truth_flights = [
        Flight.model_construct(**flight)
        for flight in ground_truth_outputs.get("expected_flights", [])
    ]
    
    predicted_flights = [
        Flight(**flight)
        for flight in outputs.get("flights", [])
    ]
    
    evaluation_results = evaluator.evaluate(ground_truth_flights, predicted_flights)
   
    langsmith_results = [
        {"key": rule, "score": int(passed)} for rule, passed in evaluation_results.items()
    ]
    
    return {"results": langsmith_results}



def main() -> None:
    """Run a rule-based evaluation via LangSmith."""
    client = Client()
    dataset_name = "wayfinder-rule-based-eval-v3"

    # LangSmith requires a dataset to exist before it will accept an experiment upload.
    # We create it if it doesn't exist, and add our single scenario.
    if not client.has_dataset(dataset_name=dataset_name):
        dataset = client.create_dataset(dataset_name=dataset_name)
        client.create_example(
            inputs={"query": "Book me a flight from Bangalore to Tokyo"},
            outputs={
                "expected_flights": [
                    {
                        "source": "Bangalore",
                        "destination": "Tokyo"
                    }
                ]
            },
            dataset_id=dataset.id,
        )

    # Execute Wayfinder against the evaluation scenario and upload
    # the evaluation results to LangSmith.
    evaluate(
        target,
        data=dataset_name,
        evaluators=[langsmith_rule_based_evaluator],
        experiment_prefix="wayfinder-rule-based",
    )

    print("Evaluation submitted to LangSmith.")


if __name__ == "__main__":
    main()
