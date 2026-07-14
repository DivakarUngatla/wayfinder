# ADR-001

## FlightService instead of MockFlightService

Decision

Use FlightService.

Reason

The service represents a business capability, not its current implementation.

Future implementations may use
- Database
- Airline APIs
- Simulators

without changing consumers.

# ADR-002

No FastAPI in Milestone 1

Decision

Start with runnable examples.

Reason

The educational focus is on the agent and evaluation pipeline.

API adapters can be added later without changing the core architecture.

# ADR-003

Do not create FlightSearchResponse

Decision

Return list[Flight].

Reason

There is no metadata yet.

Introduce a response object only when pagination, warnings or statistics are needed.
# ADR-003
Decision: Wayfinder uses industry-standard AI engineering tools rather than reimplementing them.

Rationale: The goal of Wayfinder is to teach engineers how to build production AI applications. We implement application-specific business logic (such as custom evaluators) and integrate with established tools like LangSmith and Langfuse when they solve real problems. This keeps the repository focused on engineering practices rather than framework implementation.