"""Wayfinder agent."""

import json
from datetime import date
from typing import Any

import openai

from wayfinder.models.agent_response import AgentResponse
from wayfinder.models.flight import Flight
from wayfinder.models.flight_search_request import FlightSearchRequest
from wayfinder.tools.search_flight_tool import SearchFlightTool

from langsmith import traceable

MODEL = "gpt-4o-mini"

_EXTRACT_FLIGHT_REQUEST_PROMPT = """\
You are a flight search assistant. Extract the flight search details from the
user's message and return them as a structured FlightSearchRequest.

Today's date is {today}.

First, determine whether the user's request is a supported flight search:

Wayfinder can ONLY help with:
- Searching for available flights between two locations.
- Comparing flights by price, duration, or arrival time.
- Finding the cheapest, fastest, or earliest-arriving flight.
- Answering questions about seat availability or flight schedules.
- Recommending or suggesting flights based on user preferences.

Wayfinder CANNOT help with:
- Booking, reserving, or purchasing flights.
- Cancelling or modifying existing bookings.
- Processing payments or redeeming miles or loyalty points.
- Weather forecasts or conditions.
- Visa or immigration requirements.
- Hotel or accommodation recommendations.
- Non-flight travel recommendations (e.g., itineraries, packing lists).
- Any other non-flight topic.

Note: General requests for flight recommendations, flight options, or flight suggestions ARE supported flight searches.

If the request is NOT a supported flight search:
- Set is_flight_search to false.
- Set rejection_response to a polite, concise explanation that acknowledges
  the request, explains it is outside Wayfinder's capabilities, and mentions
  that Wayfinder can help search and compare flights.
- Leave source, destination, and other flight fields as empty strings / defaults.

If the request IS a supported flight search:
- Set is_flight_search to true.
- Set rejection_response to null.
- Extract the flight details using the rules below.

Extraction rules (apply only when is_flight_search is true):
- source: the departure city or airport explicitly provided by the user
  (e.g. "Bangalore", "BLR").
- destination: the arrival city or airport explicitly provided by the user
  (e.g. "Tokyo", "NRT").
- Never assume, infer, or invent source or destination.
- If the user does not provide source, return an empty string for source.
- If the user does not provide destination, return an empty string for
  destination.
- departure_date: the requested departure date in ISO 8601 format (YYYY-MM-DD).
  Resolve relative expressions such as "today", "tomorrow", or "next Friday"
  using today's date above. If no date is mentioned, use today's date.
- passengers: the number of passengers. If not mentioned, default to 1.
"""

_GENERATE_RESPONSE_PROMPT = """
You are Wayfinder, an AI flight search assistant.

The flight search has already been completed using the user's constraints.
The retrieved flight results have already been filtered and sorted according to the user's request.

You are given:
1. the user's request
2. retrieved flight results

Your task is to answer the user's request using ONLY the retrieved flight results.

Before responding:
- Read all retrieved flights completely.
- If multiple flights are provided, mention all relevant options.

Never:
- invent flights
- invent prices
- claim no flights match unless the retrieved flights list is empty

If no flights are returned, clearly state that no matching flights were found.
"""

_CLARIFY_MISSING_FIELDS_PROMPT = """
You are Wayfinder, an AI flight search assistant.

The user's flight request cannot be searched yet because required information
is missing.

Your task is ONLY to ask a concise, natural clarification question that obtains
the missing information.

Rules:
- Ask only for information listed as missing.
- Do not invent, assume, or infer missing information.
- Do not search for flights.
- Do not provide flight recommendations.
- Do not provide flight results.
- If multiple required fields are missing, ask for all of them in one natural
  question.
- If only one field is missing, ask only for that field.
- Use natural language rather than referring to internal field names such as
  "source" or "destination".
- Do not mention validation, extraction, schemas, tools, or internal logic.
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

    def _clarify_missing_fields(
        self, user_query: str, request: FlightSearchRequest, missing: list[str]
    ) -> AgentResponse:
        """Ask the user for missing required fields using an LLM.

        Called by the validation gate when source or destination is absent.
        Returns an AgentResponse with an empty flights list and a
        natural-language clarification question.
        """
        missing_block = "\n".join(f"- {field}" for field in missing)

        clarification = self._client.chat.completions.create(
            model=MODEL,
            messages=[
                {
                    "role": "system",
                    "content": _CLARIFY_MISSING_FIELDS_PROMPT,
                },
                {
                    "role": "user",
                    "content": (
                        f"User request: {user_query}\n\n"
                        f"Extracted so far:\n"
                        f"  source: {request.source!r}\n"
                        f"  destination: {request.destination!r}\n\n"
                        f"Missing required fields:\n{missing_block}"
                    ),
                },
            ],
        )

        clarification_text = clarification.choices[0].message.content or ""
        return AgentResponse(flights=[], response=clarification_text)

    @traceable(name="WayfinderAgent")
    def run(self, user_query: str, **kwargs: Any) -> AgentResponse:
        """Process a user query and return an AgentResponse.

        Step 1: LLM extraction — parses a FlightSearchRequest that includes
                inline intent classification. Unsupported requests (weather,
                visa, hotels, booking, payment, etc.) are rejected here before
                the flight search tool is ever invoked.
        Step 1b: Deterministic validation gate — if source or destination is
                 missing, an LLM clarification step asks for the missing
                 information and stops without calling the search tool.
        Step 2: Flight search tool.
        Step 3: LLM response generation from retrieved results.

        Returns an AgentResponse containing both the structured flights and
        the natural-language reply.
        """
        # --- Step 1: Extract FlightSearchRequest (includes intent classification) ---
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

        # --- Capability gate: reject unsupported requests ---
        if not request.is_flight_search:
            response_text = request.rejection_response or (
                "I can only help with searching and comparing flights. "
                "Let me know if you'd like to look up available flights!"
            )
            return AgentResponse(flights=[], response=response_text)

        # --- Validation gate: require source and destination ---
        # The LLM returns an empty string for required str fields it could
        # not extract.  Check both before invoking the search tool.
        missing_source = not request.source.strip()
        missing_destination = not request.destination.strip()

        missing: list[str] = []
        if missing_source:
            missing.append("source: departure city or airport")
        if missing_destination:
            missing.append("destination: arrival city or airport")

        if missing:
            return self._clarify_missing_fields(user_query, request, missing)

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