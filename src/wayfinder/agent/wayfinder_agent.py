"""Wayfinder agent."""

import json
from datetime import date

import openai

from wayfinder.models.agent_response import AgentResponse
from wayfinder.models.flight import Flight
from wayfinder.models.flight_search_request import FlightSearchRequest
from wayfinder.tools.search_flight_tool import SearchFlightTool

MODEL = "gpt-4o-mini"

_EXTRACT_FLIGHT_REQUEST_PROMPT = """\
You are a flight search assistant. Extract the flight search details from the
user's message and return them as a structured FlightSearchRequest.

Today's date is {today}.

Rules:
- source: the departure city or airport (e.g. "Bangalore", "BLR").
- destination: the arrival city or airport (e.g. "Tokyo", "NRT").
- departure_date: the requested departure date in ISO 8601 format (YYYY-MM-DD).
  Resolve relative expressions such as "today", "tomorrow", or "next Friday"
  using today's date above. If no date is mentioned, use today's date.
- passengers: the number of passengers. If not mentioned, default to 1.
"""

_GENERATE_RESPONSE_PROMPT = """
You are Wayfinder, an AI flight search assistant.

Wayfinder helps users search and compare available flights.

Wayfinder does NOT book, reserve, pay for, modify, or cancel flights.

The flight search has already been completed.

You are given:
1. the user's request
2. the retrieved flight results

Your job is to answer the user's request naturally using only the retrieved results.

If the user asked for the cheapest, fastest, or shortest flight, identify it from the retrieved results.

If no flights are available, explain that clearly.

Do not invent information that is not present in the retrieved results.
"""

class WayfinderAgent:
    """Orchestrates flight search using an LLM to parse the user's query
    and generate a natural-language response from the results."""

    def __init__(
        self,
        search_flight_tool: SearchFlightTool,
        client: openai.OpenAI,
    ) -> None:
        """Initialize the agent with a flight search tool and an OpenAI client."""
        self._search_flight_tool = search_flight_tool
        self._client = client

    def run(self, user_query: str) -> AgentResponse:
        """Process a user query and return an AgentResponse.

        Step 1: Uses an LLM to extract a structured FlightSearchRequest from
                the natural-language query.
        Step 2: Delegates to the flight search tool.
        Step 3: Uses a second LLM call to generate a natural-language response
                from the structured results.

        Returns an AgentResponse containing both the structured flights and
        the natural-language reply. When the query cannot be understood,
        flights is empty and response contains a helpful error message.
        """
        # --- Step 1: Extract FlightSearchRequest from the user query ---
        system_prompt = _EXTRACT_FLIGHT_REQUEST_PROMPT.format(
            today=date.today().isoformat()
        )

        extraction = self._client.beta.chat.completions.parse(
            model=MODEL,
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_query},
            ],
            response_format=FlightSearchRequest,
        )

        request = extraction.choices[0].message.parsed

        if request is None:
            return AgentResponse(
                flights=[],
                response="I could not understand your flight request. Please try again.",
            )

        # --- Step 2: Search for flights ---
        flights: list[Flight] = self._search_flight_tool.search(request)

        # --- Step 3: Generate a natural-language response ---
        flights_json = json.dumps(
            [f.model_dump(mode="json") for f in flights],
            indent=2,
        )

        generation = self._client.chat.completions.create(
            model=MODEL,
            messages=[
                {
                    "role": "system",
                    "content": _GENERATE_RESPONSE_PROMPT,
                },
                {
                    "role": "user",
                    "content": user_query,
                },
                {
                    "role": "system",
                    "content": f"""
            The flight search has already been completed.

            The following JSON contains the retrieved flight results.

            Use ONLY these results to answer the user's request.

            {flights_json}
            """,
                },
            ]
        )

        response_text = generation.choices[0].message.content or ""

        return AgentResponse(flights=flights, response=response_text)