# Wayfinder

Wayfinder is a reference implementation for exploring, learning, and teaching AI Engineering through a realistic AI travel assistant.

It evolves alongside the **AI Engineering Fundamentals** article series, with each milestone introducing one new AI Engineering concept and its implementation.

---

## Why Wayfinder?

Most AI tutorials focus on frameworks.

Wayfinder focuses on **engineering principles**.

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

### ✅ Milestone 1 — Basic Flight Search

Implemented:

- Flight domain models
- Flight search service
- Search flight tool
- Wayfinder agent
- Runnable example

---

## Project Structure

```text
src/
    wayfinder/
        agent/
        models/
        services/
        tools/

examples/
docs/
```

---

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

Run the first example:

```bash
uv run python examples/basic_flight_search.py
```

---

## Learning Journey

- ✅ Milestone 1 — Basic Flight Search
- 🚧 Milestone 2 — Rule-Based Evaluation
- ⏳ Milestone 3 — LLM Integration
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