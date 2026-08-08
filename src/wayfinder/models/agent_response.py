"""Agent response models."""

from pydantic import BaseModel, Field

from wayfinder.models.flight import Flight


class AgentResponse(BaseModel):
    """Response produced by WayfinderAgent for a user query."""

    flights: list[Flight] = Field(
        description="Structured flight options returned by the flight search tool."
    )
    response: str = Field(
        description="Natural-language reply shown to the user."
    )
