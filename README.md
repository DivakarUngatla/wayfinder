# Wayfinder

Wayfinder is a reference implementation for exploring, learning, and teaching AI Engineering through a realistic AI travel assistant.

It evolves alongside the **AI Engineering Fundamentals** article series, with each milestone introducing one new AI Engineering concept and its implementation.

---

## Why Wayfinder?

Many AI tutorials begin by introducing frameworks.

Wayfinder starts with engineering principles and introduces frameworks only when they solve a real problem.

Instead of introducing every AI framework at once, the project evolves incrementally—building one concept at a time while keeping the codebase runnable and easy to understand.

---

## Engineering Principles

Wayfinder follows a few simple principles:

- Teach concepts before frameworks.
- Introduce technologies only when they solve a real problem.
- Build one concept at a time.
- Keep the architecture framework-neutral.
- Prefer readability over cleverness.
- Earn abstractions instead of designing them upfront.
- End every milestone with a runnable example.

---

## Current Milestone

### ✅ Milestone 2 — Rule-Based Evaluation

Implemented:

- Flight domain models
- Flight search service
- Search flight tool
- Wayfinder agent
- Runnable example
- Rule-based evaluator (in progress)

> **Note**
>
> The current `WayfinderAgent` intentionally uses simple rule-based parsing.
> This keeps the focus on learning AI engineering concepts such as evaluation,
> rather than prompt engineering or LLM orchestration. As the series progresses,
> the agent will evolve into a more capable AI-powered implementation while
> reusing the same evaluation framework.
---

## Project Structure

```text
src/
    wayfinder/
        agent/
        evaluators/
        models/
        services/
        tools/

examples/
docs/
```

---
## LangSmith Setup

The LangSmith evaluation example requires a LangSmith account and an API key.

1. Create a LangSmith account and generate an API key by following the official guide:
   https://docs.langchain.com/langsmith/create-account-api-key

2. Copy the example environment file:

```bash
cp .env.example .env
```

3. Replace the placeholder value in `.env` with your own API key.

The LangSmith evaluation example automatically loads the `.env` file using `python-dotenv`.

> **Note**
>
> The local rule-based evaluation example does **not** require LangSmith or any API keys. Only the `langsmith_evaluation.py` example depends on this configuration.

## Quick Start

Clone the repository:

```bash
git clone https://github.com/DivakarUngatla/wayfinder.git

cd wayfinder
```

Install dependencies:

```bash
uv sync
```

Run the basic flight search example:

```bash
uv run python examples/basic_flight_search.py
```

Run the local rule-based evaluation:

```bash
uv run python examples/local_evaluation.py
```

Run the LangSmith evaluation (requires LangSmith API credentials):

```bash
uv run python examples/langsmith_evaluation.py
```

---

## Learning Journey

- ✅ Milestone 1 — Basic Flight Search
- ✅ Milestone 2 — Rule-Based Evaluation
- ⏳ Milestone 3 — LLM-Powered Flight Search
- ⏳ Milestone 4 — Human Evaluation
- ⏳ Milestone 5 — LLM-as-a-Judge
- ⏳ Milestone 6 — Building an AI Evaluation Framework
- ⏳ Milestone 7 — AI Evaluation Tools & Observability

---

## Documentation

- `docs/architecture.md`
- `docs/coding_principles.md`
- `docs/design_decisions.md`

---

## AI Engineering Fundamentals Series

Wayfinder evolves alongside the **AI Engineering Fundamentals** series.

Each article introduces one new engineering concept, and the repository implements it step by step.

The goal is not to build a production travel platform.

The goal is to demonstrate production AI engineering practices through a realistic application.

## Releases

Each milestone in the AI Engineering Fundamentals series is published as a GitHub Release.

If you're following along with an article, check out the corresponding release to see the exact code used in that milestone.

| Milestone | Release |
|-----------|---------|
| Basic Flight Search | v0.1.0 |
| Rule-Based Evaluation | v0.2.0 |
| ... | ... |