"""Wayfinder interactive terminal assistant.

Starts an interactive chat session in the terminal. Each user message is
processed by WayfinderAgent, which returns a natural-language response and
structured flight results.

Usage:
    uv run python examples/wayfinder_cli.py
"""

import uuid

import openai
from dotenv import load_dotenv
from langsmith import Client
from rich.console import Console
from rich.text import Text

from wayfinder.agent.wayfinder_agent import WayfinderAgent
from wayfinder.models.flight import Flight
from wayfinder.services.flight_service import FlightService
from wayfinder.tools.search_flight_tool import SearchFlightTool

load_dotenv()

console = Console(highlight=False)

_DIVIDER = "-" * 50
_HEADER = "=" * 50


def print_flights(flights: list[Flight]) -> None:
    """Print retrieved flight results in the same format as basic_flight_search.py."""
    console.print(f"  Found {len(flights)} flight(s):\n")
    for flight in flights:
        console.print(f"  {flight.airline} · {flight.flight_number}")
        console.print(f"  Route     : {flight.source} → {flight.destination}")
        console.print(f"  Departure : {flight.departure_time.strftime('%d %b %Y %H:%M')}")
        console.print(f"  Arrival   : {flight.arrival_time.strftime('%d %b %Y %H:%M')}")
        console.print(f"  Duration  : {flight.duration}")
        console.print(f"  Price     : {flight.currency} {flight.price:,.2f}")
        console.print(f"  Seats     : {flight.available_seats} available")
        console.print()


def print_startup() -> None:
    """Print the startup screen."""
    console.print()
    console.print(_HEADER)
    console.print(Text("✈️  Wayfinder", style="bold blue"))
    console.print("AI Flight Assistant")
    console.print(_HEADER)
    console.print()
    console.print("Search, compare and explore flights using natural language.")
    console.print()
    console.print("[dim]Examples:[/dim]")
    console.print("  • Find the cheapest flight from Bangalore to Tokyo.")
    console.print("  • Show flights from Bangalore to Tokyo tomorrow.")
    console.print("  • Which flight arrives before 8 PM?")
    console.print("  • Book me a business class ticket.")
    console.print()
    console.print("[dim]Type 'exit' or 'quit' to leave.[/dim]")
    console.print(_DIVIDER)


def print_response(response: str, flights: list[Flight]) -> None:
    """Print the assistant response followed by the raw flight tool output.

    The two sections use different colors to make it clear that the assistant
    response is the LLM-generated reply, while the tool output is the raw
    structured data returned by the flight search tool before the LLM
    generated its answer.
    """
    # --- Assistant response (green) ---
    console.print()
    console.print("[bold green]Assistant[/bold green]")
    console.print("[green]---------[/green]")
    console.print(Text(response, style="green"))
    console.print()

    # --- Flight search tool output (dim / default) ---
    console.print("[bold]Flight Search Tool Output[/bold]")
    console.print("-------------------------")
    if flights:
        print_flights(flights)
    else:
        console.print("  No flights returned.\n")


def build_agent() -> WayfinderAgent:
    """Construct and return a WayfinderAgent instance."""
    flight_service = FlightService()
    search_flight_tool = SearchFlightTool(flight_service=flight_service)
    return WayfinderAgent(
        search_flight_tool=search_flight_tool,
        client=openai.OpenAI(),
    )


def chat(agent: WayfinderAgent) -> None:
    """Run the interactive chat loop.

    Accepts user input until the user types 'exit' or 'quit'.
    Each query is forwarded to WayfinderAgent.run(). The same agent instance
    is reused across turns, which makes it straightforward to introduce
    conversation history in a future milestone without changing this loop.
    """
    while True:
        console.print()
        try:
            user_input = console.input("[cyan]You >[/cyan] ").strip()
        except EOFError:
            break

        if not user_input:
            continue

        if user_input.lower() in {"exit", "quit"}:
            break

        try:
            run_id = uuid.uuid4()
            result = agent.run(user_input, langsmith_extra={"run_id": run_id})
        except Exception as e:
            console.print(f"\n[red]Error:[/red] {e}\n")
            console.print(_DIVIDER)
            continue

        print_response(result.response, result.flights)

        # Collect user feedback
        console.print(f"  [dim]{'─' * 37}[/dim]")
        console.print("  [bold cyan]💬 Feedback[/bold cyan]")
        feedback = console.input("  [cyan]Was this response helpful?[/cyan] [dim](y/n):[/dim] ").strip().lower()
        if feedback in {"y", "n"}:
            score = 1 if feedback == "y" else 0
            comment = "thumbs_up" if score == 1 else "thumbs_down"
            try:
                ls_client = Client()
                ls_client.create_feedback(
                    run_id=run_id,
                    key="user_feedback",
                    score=score,
                    comment=comment
                )
                console.print("  [dim]Thank you for your feedback![/dim]")
            except Exception as e:
                console.print(f"  [dim red]Failed to submit feedback to LangSmith: {e}[/dim red]")
        else:
            console.print("  [dim]Feedback skipped.[/dim]")

        console.print(_DIVIDER)


def main() -> None:
    """Start the Wayfinder interactive assistant."""
    print_startup()

    agent = build_agent()

    try:
        chat(agent)
    except KeyboardInterrupt:
        pass

    console.print()
    console.print("Thanks for trying Wayfinder!")
    console.print("Goodbye!")
    console.print()


if __name__ == "__main__":
    main()
