"""LLM-as-a-Judge local evaluation example for Wayfinder.

Runs the Wayfinder agent live for every sample in the evaluation dataset,
then sends the freshly generated response and retrieved flight data to
LLMJudge. No pre-stored responses are used.

This is the local LLM-as-a-Judge demo.

After the per-criterion summary, a Failure Analysis section highlights
samples where the overall score or any individual criterion score is below 4,
grouped by dataset category.

Usage:
    uv run python examples/llm_as_a_judge/local_evaluation.py
"""

import json
from collections import defaultdict
from dataclasses import dataclass
from pathlib import Path

import openai
from dotenv import load_dotenv
from rich.console import Console

from wayfinder.agent.wayfinder_agent import WayfinderAgent
from wayfinder.evaluators.criteria import CRITERIA
from wayfinder.evaluators.llm_judge import LLMJudge
from wayfinder.models.flight import Flight
from wayfinder.models.judge_result import JudgeResult
from wayfinder.services.flight_service import FlightService
from wayfinder.tools.search_flight_tool import SearchFlightTool

load_dotenv()

DATASET_FILE = (
    Path(__file__).parent / "wayfinder_llm_judge_evaluation_v1.jsonl"
)

FAILURE_THRESHOLD = 4  # A score strictly below this is considered a failure.

console = Console(highlight=False)


# ---------------------------------------------------------------------------
# Structured result container
# ---------------------------------------------------------------------------

@dataclass
class EvaluatedSample:
    """Captures everything produced during a single live evaluation run."""

    id: str
    category: str
    query: str
    expected_behavior: str
    response: str
    retrieved_flights: list[Flight]
    result: JudgeResult

    def is_failure(self) -> bool:
        """Return True if the overall score or any criterion score is below the threshold."""
        if self.result.overall_score < FAILURE_THRESHOLD:
            return True
        return any(cs.score < FAILURE_THRESHOLD for cs in self.result.criteria_scores)

    def weak_criteria(self):
        """Return criterion scores that fall below the failure threshold."""
        return [cs for cs in self.result.criteria_scores if cs.score < FAILURE_THRESHOLD]


# ---------------------------------------------------------------------------
# Setup helpers
# ---------------------------------------------------------------------------

def load_dataset() -> list[dict]:
    """Load the evaluation dataset from disk.

    Extracts inputs and expected outputs for the LLM judge.
    """
    samples = []
    with open(DATASET_FILE, "r", encoding="utf-8") as f:
        for line in f:
            if line.strip():
                samples.append(json.loads(line))
    return samples


def build_agent(client: openai.OpenAI) -> WayfinderAgent:
    """Construct and return a WayfinderAgent instance."""
    flight_service = FlightService()
    search_flight_tool = SearchFlightTool(flight_service=flight_service)
    return WayfinderAgent(search_flight_tool=search_flight_tool, client=client)


# ---------------------------------------------------------------------------
# Printing helpers
# ---------------------------------------------------------------------------

def print_sample_result(index: int, sample: dict, result: JudgeResult) -> None:
    """Print the judge's scores and explanations for one sample."""
    console.print(f"\n[bold]Sample {index} — {sample['metadata']['id']}[/bold]")
    console.print(f"[dim]Category:[/dim] {sample['metadata']['category']}")
    console.print(f"[dim]Query:[/dim] {sample['inputs']['query']}")
    console.print()

    console.print("[bold]Criteria Scores[/bold]")
    for cs in result.criteria_scores:
        score_color = "green" if cs.score >= FAILURE_THRESHOLD else "red"
        console.print(
            f"  [cyan]{cs.criterion}[/cyan]  "
            f"score: [bold {score_color}]{cs.score}[/bold {score_color}]/5"
        )
        console.print(f"  {cs.explanation}")
        console.print()

    overall_color = "green" if result.overall_score >= FAILURE_THRESHOLD else "red"
    console.print(
        f"[bold]Overall Score:[/bold] "
        f"[bold {overall_color}]{result.overall_score}[/bold {overall_color}]/5"
    )
    console.print(f"{result.overall_explanation}")
    console.print("[dim]" + "-" * 60 + "[/dim]")


def print_summary(scores_by_criterion: dict[str, list[int]], overall_scores: list[int]) -> None:
    """Print the mean score per criterion and the mean overall score."""
    console.print("\n[bold]Evaluation Summary[/bold]")
    console.print("[dim]" + "=" * 60 + "[/dim]")

    for name in [c.name for c in CRITERIA]:
        scores = scores_by_criterion.get(name, [])
        if scores:
            mean = sum(scores) / len(scores)
            console.print(f"  {name:<25} avg: [bold]{mean:.2f}[/bold]/5")

    console.print()
    if overall_scores:
        overall_mean = sum(overall_scores) / len(overall_scores)
        console.print(
            f"  {'Overall':<25} avg: [bold green]{overall_mean:.2f}[/bold green]/5"
        )

    console.print()


def print_failure_analysis(failures: list[EvaluatedSample]) -> None:
    """Print detailed failure analysis for every failed sample."""
    console.print("[bold]Failure Analysis[/bold]")
    console.print("[dim]" + "=" * 60 + "[/dim]")

    if not failures:
        console.print("  [green]No failures detected.[/green]\n")
        return

    console.print(
        f"  [red]{len(failures)} sample(s) scored below {FAILURE_THRESHOLD} "
        f"on overall score or at least one criterion.[/red]\n"
    )

    for ev in failures:
        console.print(f"[bold red]{ev.id}[/bold red]")
        console.print(f"Category: {ev.category}")
        console.print(f"Query: {ev.query}")
        console.print(f"Overall: [bold red]{ev.result.overall_score}[/bold red]/5")
        console.print()

        console.print("[dim]Expected behavior:[/dim]")
        console.print(f"  {ev.expected_behavior}")
        console.print()

        weak = ev.weak_criteria()
        if weak:
            console.print("[dim]Weak criteria:[/dim]")
            for cs in weak:
                console.print(f"  [cyan]{cs.criterion}[/cyan]: [red]{cs.score}[/red]/5")
                console.print(f"  {cs.explanation}")
            console.print()

        console.print("[dim]Judge explanation:[/dim]")
        console.print(f"  {ev.result.overall_explanation}")
        console.print()

        console.print("[dim]Agent response:[/dim]")
        console.print(f"  {ev.response}")
        console.print()


def print_failures_by_category(failures: list[EvaluatedSample]) -> None:
    """Print the count of failed samples grouped by dataset category."""
    console.print("[bold]Failures by Category[/bold]")
    console.print("[dim]" + "=" * 60 + "[/dim]")

    if not failures:
        console.print("  [green]No failures.[/green]\n")
        return

    counts: dict[str, int] = defaultdict(int)
    for ev in failures:
        counts[ev.category] += 1

    for category, count in sorted(counts.items(), key=lambda x: -x[1]):
        console.print(f"  {category:<30} {count}")

    console.print()


# ---------------------------------------------------------------------------
# Main evaluation loop
# ---------------------------------------------------------------------------

def main() -> None:
    """Run the live LLM-as-a-Judge evaluation."""
    console.print("[bold blue]✈  Wayfinder[/bold blue]")
    console.print("[bold]LLM-as-a-Judge — Local Evaluation[/bold]")
    console.print(
        "[yellow]Agent runs live for each sample. Responses are freshly generated.[/yellow]"
    )
    console.print()

    samples = load_dataset()
    openai_client = openai.OpenAI()
    agent = build_agent(openai_client)
    judge = LLMJudge(client=openai_client)

    scores_by_criterion: dict[str, list[int]] = defaultdict(list)
    overall_scores: list[int] = []
    evaluated: list[EvaluatedSample] = []

    for i, sample in enumerate(samples, start=1):
        query = sample["inputs"]["query"]
        expected_behavior = sample["outputs"]["expected_behavior"]

        console.print(f"[dim]Running agent [{i}/{len(samples)}] {sample['metadata']['id']}...[/dim]")

        # Run the agent live — response and flights are freshly generated.
        agent_result = agent.run(query)
        response = agent_result.response
        retrieved_flights = agent_result.flights

        console.print(
            f"[dim]  → {len(retrieved_flights)} flight(s) retrieved · "
            f"evaluating with judge...[/dim]"
        )

        result = judge.evaluate(
            query=query,
            expected_behavior=expected_behavior,
            response=response,
            context=retrieved_flights,
        )

        for cs in result.criteria_scores:
            scores_by_criterion[cs.criterion].append(cs.score)
        overall_scores.append(result.overall_score)

        ev = EvaluatedSample(
            id=sample["metadata"]["id"],
            category=sample["metadata"]["category"],
            query=query,
            expected_behavior=expected_behavior,
            response=response,
            retrieved_flights=retrieved_flights,
            result=result,
        )
        evaluated.append(ev)

        print_sample_result(i, sample, result)

    # --- Aggregate summary (unchanged from original) ---
    print_summary(scores_by_criterion, overall_scores)

    # --- Failure analysis (new) ---
    failures = [ev for ev in evaluated if ev.is_failure()]
    print_failure_analysis(failures)
    print_failures_by_category(failures)


if __name__ == "__main__":
    main()
