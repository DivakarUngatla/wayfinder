import os
import argparse
from rich.console import Console
from rich.panel import Panel
from langsmith import Client, evaluate
from openai import OpenAI

from wayfinder.agent.wayfinder_agent import WayfinderAgent
from wayfinder.services.flight_service import FlightService
from wayfinder.tools.search_flight_tool import SearchFlightTool

from wayfinder.evaluators.llm_judge import LLMJudge

def main():
    parser = argparse.ArgumentParser(description="Run Wayfinder experiment comparison.")
    parser.add_argument("--dataset-name", type=str, default="wayfinder_experiment_comparison", help="LangSmith dataset name to use or create")
    parser.add_argument("--prefix", type=str, required=True, help="Experiment prefix name (e.g., wayfinder-baseline)")
    parser.add_argument("--repetitions", type=int, default=5, help="Number of evaluation repetitions per example")
    args = parser.parse_args()

    console = Console()
    
    # Initialize application components
    flight_service = FlightService()
    search_tool = SearchFlightTool(flight_service)
    openai_client = OpenAI()
    agent = WayfinderAgent(
        search_flight_tool=search_tool,
        client=openai_client,
    )
    
    ls_client = Client()
    
    # 1. Sync the dataset to LangSmith
    dataset_name = args.dataset_name
    dataset_path = "examples/experiment_comparison/dataset/wayfinder_experiment_comparison_v1.jsonl"
    
    if not ls_client.has_dataset(dataset_name=dataset_name):
        console.print(f"Creating dataset [bold]{dataset_name}[/bold]...")
        dataset = ls_client.create_dataset(
            dataset_name=dataset_name,
            description="Focused 2-case dataset for comparing baseline vs deterministic filtering.",
        )
        # Import JSONL
        import json
        with open(dataset_path, "r") as f:
            for line in f:
                if not line.strip(): continue
                data = json.loads(line)
                ls_client.create_example(
                    inputs={"query": data["query"]},
                    outputs={"expected_behavior": data["expected_behavior"]},
                    dataset_id=dataset.id,
                )
    
    # 2. Define the target function for LangSmith
    def target(inputs: dict, langsmith_extra: dict = None) -> dict:
        """The function evaluated by LangSmith."""
        result = agent.run(inputs["query"])
        
        # Serialize flights for the evaluator
        flights_dict = [f.model_dump() for f in result.flights]
        
        return {
            "response": result.response,
            "retrieved_flights": flights_dict,
        }
        
    # 3. Define the evaluator using existing LLMJudge
    judge = LLMJudge(client=openai_client)
    
    def langsmith_llm_judge_evaluator(run, example) -> dict:
        """Evaluator wrapping the existing WayfinderLLMJudge."""
        expected_behavior = example.outputs.get("expected_behavior")
        actual_response = run.outputs.get("response")
        retrieved_flights = run.outputs.get("retrieved_flights", [])
        
        judge_result = judge.evaluate(
            query=example.inputs["query"],
            context=retrieved_flights,
            response=actual_response,
            expected_behavior=expected_behavior
        )
        
        # Build a dict for easy lookup
        scores_dict = {c.criterion.lower().replace(" ", "_"): c for c in judge_result.criteria_scores}
        
        # Safe lookup helper
        def get_score(key):
            return scores_dict[key].score if key in scores_dict else 0
        def get_comment(key):
            return scores_dict[key].explanation if key in scores_dict else ""

        
        # Log to LangSmith
        return {
            "key": "llm_judge",
            "score": judge_result.overall_score,
            "comment": judge_result.overall_explanation,
            "results": [
                {"key": "helpfulness", "score": get_score('helpfulness'), "comment": get_comment('helpfulness')},
                {"key": "relevance", "score": get_score('relevance'), "comment": get_comment('relevance')},
                {"key": "clarity", "score": get_score('clarity'), "comment": get_comment('clarity')},
                {"key": "completeness", "score": get_score('completeness'), "comment": get_comment('completeness')},
                {"key": "groundedness", "score": get_score('groundedness'), "comment": get_comment('groundedness')},
                {"key": "instruction_following", "score": get_score('instruction_following'), "comment": get_comment('instruction_following')},
            ]
        }
        
    # 4. Run the experiment
    num_examples = 0
    with open(dataset_path, "r") as f:
        for line in f:
            if line.strip():
                num_examples += 1
                
    summary_text = f"""[bold cyan]✈ Wayfinder Experiment Comparison[/bold cyan]

Dataset:      {dataset_name}
Experiment:   {args.prefix}
Examples:     {num_examples}
Repetitions:  {args.repetitions}

Running evaluation..."""
    console.print()
    console.print(Panel(summary_text, expand=False))
    console.print()

    evaluate(
        target,
        data=dataset_name,
        evaluators=[langsmith_llm_judge_evaluator],
        experiment_prefix=args.prefix,
        num_repetitions=args.repetitions
    )
    
    completion_text = """[bold green]✓ Experiment completed successfully[/bold green]

Open the LangSmith experiment above
to inspect and compare the results."""
    console.print()
    console.print(Panel(completion_text, title="Wayfinder", expand=False))


if __name__ == "__main__":
    import dotenv
    dotenv.load_dotenv()
    main()
