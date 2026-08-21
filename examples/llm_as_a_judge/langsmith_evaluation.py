"""LangSmith evaluation example for LLM-as-a-Judge.

Demonstrates how to execute the existing LLMJudge using LangSmith.
"""

from typing import Any

from rich.console import Console
from rich.panel import Panel

from dotenv import load_dotenv
from openai import OpenAI
from langsmith import evaluate

from wayfinder.agent.wayfinder_agent import WayfinderAgent
from wayfinder.evaluators.llm_judge import LLMJudge
from wayfinder.models.flight import Flight
from wayfinder.services.flight_service import FlightService
from wayfinder.tools.search_flight_tool import SearchFlightTool

load_dotenv()

# --- Shared instances (constructor injection) ---
flight_service = FlightService()
search_flight_tool = SearchFlightTool(flight_service=flight_service)
client = OpenAI()
agent = WayfinderAgent(search_flight_tool=search_flight_tool, client=client)
judge = LLMJudge(client=client)


def target(inputs: dict[str, Any]) -> dict[str, Any]:
    """Invoke the agent with a user query and return the results."""
    result = agent.run(inputs["query"])
    return {
        "response": result.response,
        "retrieved_flights": [
            f.model_dump(mode="json")
            for f in result.flights
        ],
    }


def langsmith_llm_judge_evaluator(
    inputs: dict[str, Any], outputs: dict[str, Any], reference_outputs: dict[str, Any] | None = None
) -> dict[str, Any]:
    """Adapt LLMJudge output to the LangSmith evaluator format."""
    eval_context = reference_outputs or {}
    expected_behavior = eval_context.get("expected_behavior", "")
    
    query = inputs.get("query", "")
    response = outputs.get("response", "")
    
    retrieved_flights = [
        Flight(**flight)
        for flight in outputs.get("retrieved_flights", [])
    ]
    
    result = judge.evaluate(
        query=query,
        expected_behavior=expected_behavior,
        response=response,
        context=retrieved_flights
    )
    
    langsmith_results = [
        {"key": cs.criterion.lower(), "score": cs.score}
        for cs in result.criteria_scores
    ]
    langsmith_results.append({"key": "overall_score", "score": result.overall_score})
    
    return {"results": langsmith_results}


def main() -> None:
    """Run an LLM-as-a-Judge evaluation via LangSmith."""
    evaluate(
        target,
        data="wayfinder_llm_judge_evaluation_v1",
        evaluators=[langsmith_llm_judge_evaluator],
        experiment_prefix="wayfinder-llm-judge"
    )
    
    console = Console()
    console.print()

    console.print(
        Panel.fit(
            "[bold green]✓ Evaluation completed successfully[/bold green]\n\n"
            "Click the LangSmith experiment URL printed above to\n"
            "inspect the evaluation results in your browser.",
            title="[bold blue]Wayfinder[/bold blue]",
            border_style="green",
            padding=(1, 2),
        )
    )

if __name__ == "__main__":
    main()
