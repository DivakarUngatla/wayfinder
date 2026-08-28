"""Standalone online evaluator for Wayfinder.

This script demonstrates an asynchronous online evaluation job that fetches
recent production traces from LangSmith and evaluates them using the 
reference-free OnlineLLMJudge. Automated scores and explanations are 
attached directly to the original trace.
"""

import os
from datetime import datetime, timedelta, timezone

from dotenv import load_dotenv
from langsmith import Client
from openai import OpenAI
from rich.console import Console

from wayfinder.evaluators.online_llm_judge import OnlineLLMJudge

load_dotenv()

console = Console(highlight=False)

def main() -> None:
    console.print("\n[bold cyan]Online Evaluation[/bold cyan]")
    console.print("[bold cyan]=================[/bold cyan]\n")

    ls_client = Client()
    project_name = os.environ.get("LANGCHAIN_PROJECT", "default")

    # Initialize the judge
    openai_client = OpenAI()
    judge = OnlineLLMJudge(client=openai_client)

    # Fetch recent root WayfinderAgent runs from the last 24 hours
    start_time = datetime.now(timezone.utc) - timedelta(days=1)
    
    try:
        runs = list(ls_client.list_runs(
            project_name=project_name,
            run_type="chain",
            name="WayfinderAgent",
            start_time=start_time,
            limit=10
        ))
    except Exception as e:
        console.print(f"[red]Failed to fetch runs from LangSmith: {e}[/red]")
        return

    stats_found = len(runs)
    stats_evaluated = 0
    stats_skipped_evaluated = 0
    stats_skipped_missing = 0
    stats_failed = 0

    console.print(f"Found {stats_found} recent Wayfinder interaction(s).")

    for run in runs:
        console.print(f"\n[dim]{'-' * 60}[/dim]")
        
        # Check if already evaluated using feedback_stats
        feedback_stats = run.feedback_stats or {}
        if "online_judge_overall" in feedback_stats:
            console.print(f"[yellow]⚠ Skipped {run.id} — already evaluated.[/yellow]")
            stats_skipped_evaluated += 1
            continue

        # Extract inputs/outputs
        inputs = run.inputs or {}
        outputs = run.outputs or {}

        query = inputs.get("user_query")
        response = outputs.get("response")
        flights = outputs.get("flights")

        # Handle malformed traces gracefully
        if query is None or response is None or flights is None:
            console.print(f"[yellow]⚠ Skipped {run.id} — missing query, response, or flights in trace.[/yellow]")
            stats_skipped_missing += 1
            continue

        console.print("[bold cyan]Evaluating[/bold cyan]")
        console.print(f'[bright_white]"{query}"[/bright_white]\n')

        try:
            # Evaluate using OnlineLLMJudge (reference-free)
            result = judge.evaluate(
                query=query,
                response=response,
                context=flights
            )
            
            def get_score_color(score: int) -> str:
                if score >= 4:
                    return "green"
                elif score == 3:
                    return "yellow"
                return "red"

            # Post feedback for each criterion
            for cs in result.criteria_scores:
                criterion_key = f"online_judge_{cs.criterion.lower()}"
                ls_client.create_feedback(
                    run_id=run.id,
                    key=criterion_key,
                    score=cs.score,
                    comment=cs.explanation
                )
                color = get_score_color(cs.score)
                console.print(f"  {cs.criterion:<22}: [{color}]{cs.score}/5[/{color}]")

            # Post overall feedback
            ls_client.create_feedback(
                run_id=run.id,
                key="online_judge_overall",
                score=result.overall_score,
                comment=result.overall_explanation
            )
            overall_color = get_score_color(result.overall_score)
            console.print(f"  [bold]Overall[/bold]:                [bold {overall_color}]{result.overall_score}/5[/bold {overall_color}]\n")

            console.print(f"[green]✓ Evaluation attached to trace {run.id}.[/green]")
            stats_evaluated += 1

        except Exception as e:
            console.print(f"[red]Evaluation failed for {run.id}: {e}[/red]")
            stats_failed += 1
            continue
            
    # Final Summary
    console.print(f"\n[dim]{'=' * 60}[/dim]")
    console.print("[bold]Evaluation Summary[/bold]\n")
    console.print(f"Recent interactions:       {stats_found}")
    console.print(f"Evaluated:                 {stats_evaluated}")
    console.print(f"Already evaluated:         {stats_skipped_evaluated}")
    console.print(f"Missing interaction data:  {stats_skipped_missing}")
    console.print(f"Failed:                    {stats_failed}")
    console.print(f"[dim]{'=' * 60}[/dim]\n")

if __name__ == "__main__":
    main()
