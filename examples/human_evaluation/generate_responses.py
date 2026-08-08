"""Human evaluation dataset generator for Wayfinder.

Loads prompts from prompts.json, runs each through WayfinderAgent, and saves
the outputs to a Markdown file for manual review and annotation.

The generated document serves as the foundation of the evaluation dataset
used throughout the AI Engineering Fundamentals series for:
  - Human Evaluation
  - LLM-as-a-Judge
  - Regression evaluation
  - Prompt comparison

Usage:
    uv run python examples/human_evaluation/generate_responses.py
"""

import json
import openai
from datetime import datetime
from pathlib import Path

from dotenv import load_dotenv

from wayfinder.agent.wayfinder_agent import WayfinderAgent
from wayfinder.models.flight import Flight
from wayfinder.services.flight_service import FlightService
from wayfinder.tools.search_flight_tool import SearchFlightTool

load_dotenv()

PROMPTS_FILE = Path(__file__).parent / "prompts.json"
OUTPUT_DIR = Path(__file__).parent / "evaluation_samples"
OUTPUT_FILE = OUTPUT_DIR / "human_evaluation_dataset.md"


def flight_table(flights: list[Flight]) -> str:
    """Format a list of flights as a Markdown table."""
    if not flights:
        return "_No flights returned._\n"

    header = (
        "| # | Airline | Flight | Departure | Arrival | Duration | Price (INR) | Seats |\n"
        "|---|---------|--------|-----------|---------|----------|-------------|-------|\n"
    )
    rows = []
    for i, f in enumerate(flights, start=1):
        rows.append(
            f"| {i} "
            f"| {f.airline} "
            f"| {f.flight_number} "
            f"| {f.departure_time.strftime('%H:%M')} "
            f"| {f.arrival_time.strftime('%H:%M')} "
            f"| {f.duration} "
            f"| {f.price:,.2f} "
            f"| {f.available_seats} |"
        )
    return header + "\n".join(rows) + "\n"


def build_markdown(samples: list[dict]) -> str:
    """Render all samples as an annotatable Markdown document."""
    lines: list[str] = [
        "# Wayfinder — Human Evaluation Dataset",
        "",
        f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M')}",
        f"Prompts: {len(samples)}",
        "",
        "> Each sample shows the user query, the expected behavior, the assistant's",
        "> natural-language response, and the retrieved flight results it was based on.",
        "> Use the Rating and Notes fields to record your evaluation.",
        "",
        "---",
        "",
        "## Evaluation Criteria",
        "",
        "Use the following definitions when rating each response.",
        "",
        "| Criterion | Definition |",
        "|-----------|------------|",
        "| Helpfulness | Did the response genuinely help the user with their request? |",
        "| Relevance | Did the response address the user's actual question without unnecessary content? |",
        "| Clarity | Was the response easy to understand and well-structured? |",
        "| Completeness | Did the response cover all relevant information the user needed? |",
        "| Groundedness | Did the response rely only on the retrieved results without inventing information? |",
        "| Instruction Following | Did the assistant satisfy the user's request while respecting the available information and system constraints? |",
        "",
        "**Instruction Following — Reviewer Guidance**",
        "",
        "When rating Instruction Following, consider:",
        "",
        "- Did the assistant answer the user's request?",
        "- Did it avoid making unsupported claims?",
        "- Did it avoid inventing information that was not present in the retrieved results?",
        "- If the request could not be fully satisfied, did it respond appropriately instead of pretending it could?",
        "",
        "---",
        "",
    ]

    for i, sample in enumerate(samples, start=1):
        lines += [
            f"## Sample {i} — `{sample['id']}`",
            "",
            f"**Category:** `{sample['category']}`",
            "",
            "**Query**",
            "",
            f"> {sample['query']}",
            "",
            "**Expected Behavior**",
            "",
            sample["expected_behavior"],
            "",
            "**Assistant Response**",
            "",
            sample["response"],
            "",
            "**Retrieved Flight Results**",
            "",
            sample["flight_table"],
            "",
            "**Rating** (1 = poor · 5 = excellent)",
            "",
            "| Criterion | Rating | Notes |",
            "|-----------|--------|-------|",
            "| Helpfulness | | |",
            "| Relevance | | |",
            "| Clarity | | |",
            "| Completeness | | |",
            "| Groundedness | | |",
            "| Instruction Following | | |",
            "",
            "### Overall Assessment",
            "",
            "| Overall Score (1–5) | |",
            "|---------------------|---|",
            "|                     |   |",
            "",
            "### Overall Comments",
            "",
            "",
            "---",
            "",
        ]

    return "\n".join(lines)


def main() -> None:
    """Load prompts, run the agent, and save the evaluation dataset."""
    # --- Load prompts ---
    prompts: list[dict] = json.loads(PROMPTS_FILE.read_text(encoding="utf-8"))

    # --- Setup agent ---
    flight_service = FlightService()
    search_flight_tool = SearchFlightTool(flight_service=flight_service)
    agent = WayfinderAgent(
        search_flight_tool=search_flight_tool,
        client=openai.OpenAI(),
    )

    print("=========================================")
    print("✈️  Wayfinder")
    print("Human Evaluation — Dataset Generator")
    print("=========================================\n")

    samples: list[dict] = []

    for i, prompt in enumerate(prompts, start=1):
        query = prompt["query"]
        print(f"[{i}/{len(prompts)}] [{prompt['category']}] {query}")

        result = agent.run(query)

        print(f"  → {len(result.flights)} flight(s) retrieved")
        print(f"  → Response: {result.response[:80].strip()}{'...' if len(result.response) > 80 else ''}")
        print()

        samples.append(
            {
                "id": prompt["id"],
                "category": prompt["category"],
                "query": query,
                "expected_behavior": prompt["expected_behavior"],
                "response": result.response,
                # Structured flight data preserved for automated evaluation.
                "retrieved_flights": [f.model_dump(mode="json") for f in result.flights],
                # Pre-rendered table for the Markdown document.
                "flight_table": flight_table(result.flights),
            }
        )

    # --- Save Markdown (for human reviewers) ---
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    OUTPUT_FILE.write_text(build_markdown(samples), encoding="utf-8")
    print(f"Markdown → {OUTPUT_FILE}")

    # --- Save JSON (for automated evaluation) ---
    json_output_file = OUTPUT_DIR / "human_evaluation_dataset.json"
    json_output_file.write_text(
        json.dumps(samples, indent=2, ensure_ascii=False),
        encoding="utf-8",
    )
    print(f"JSON     → {json_output_file}")

    print(f"\n{len(samples)} sample(s) saved.")


if __name__ == "__main__":
    main()
