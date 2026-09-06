# Wayfinder

**A reference implementation for learning and building AI evaluation systems.**

[📖 Start the AI Evaluation Series](https://ai.plainenglish.io/software-tests-vs-ai-evals-why-ai-applications-need-a-different-way-of-testing-205b6ae197fb?sharedUserId=divakar.ungatla)
• [💻 GitHub Releases](https://github.com/DivakarUngatla/wayfinder/releases)
• [🐛 Report an Issue](https://github.com/DivakarUngatla/wayfinder/issues)

Wayfinder is a reference implementation for building and understanding AI evaluation systems.

It evolves a single AI-powered flight search application through rule-based evaluation, human evaluation, LLM-as-a-Judge, online evaluation, and experiment comparison.

The repository was built alongside the **AI Engineering Fundamentals — AI Evaluation** article series, with each stage introducing the next layer of the evaluation system.

## What This Repository Covers

```text
Software Tests vs AI Evals
        ↓
Evaluation Fundamentals
        ↓
Rule-Based Evaluation
        ↓
Human Evaluation
        ↓
LLM-as-a-Judge
        ↓
Online Evaluation
        ↓
Evaluation Experiments
```

Each stage builds on the same Wayfinder application, showing how an evaluation system can evolve as an AI application moves from development toward production.

# Why Wayfinder?

Building an AI application is only the beginning.

The real engineering challenge is answering questions like:

- Is my AI application improving?
- Did my latest change introduce regressions?
- How do I evaluate subjective qualities like helpfulness or groundedness?
- How can I scale evaluations beyond manual review?
- How do I confidently ship AI applications to production?

Wayfinder explores these questions through practical implementations of modern AI evaluation techniques.

# What's Implemented

- AI-powered flight search reference application
- Rule-Based Evaluation
- Human Evaluation
- LLM-as-a-Judge
- Online Evaluation
- Real user interaction tracing and explicit feedback
- Reference-free evaluation of production interactions
- Evaluation datasets and scoring rubrics
- LangSmith tracing and evaluation integration
- Evaluation experiment comparison
- Target and regression-guard evaluation cases
- Repeated evaluation runs

# Project Structure

```text
src/
└── wayfinder/
    ├── agent/
    ├── evaluators/
    ├── models/
    ├── services/
    └── tools/

examples/
├── wayfinder_cli.py
├── rule_based_evaluation/
├── human_evaluation/
├── llm_judge_evaluation/
├── online_evaluation/
└── experiment_comparison/
```

# Prerequisites

- Python 3.12+
- uv

Clone the repository:

```bash
git clone https://github.com/DivakarUngatla/wayfinder.git
cd wayfinder
```

Install dependencies:

```bash
uv sync
```

# Configuration

Copy the example environment file.

```bash
cp .env.example .env
```

## OpenAI API Key

The interactive Wayfinder assistant and Human Evaluation examples use OpenAI models.

Create an API key:

https://platform.openai.com/api-keys

Then update your `.env` file.

```text
OPENAI_API_KEY=your_api_key
```

> **Note**
>
> OpenAI is only required for examples that generate AI responses.

## LangSmith

LangSmith is required for interaction tracing and the LangSmith-based evaluation examples, including Online Evaluation and Experiment Comparison.

Create an account and API key:

https://docs.langchain.com/langsmith/create-account-api-key

Then update your `.env` file.

```text
LANGSMITH_API_KEY=your_api_key
LANGSMITH_PROJECT=wayfinder
```

# Quick Start

## Launch the AI Assistant

```bash
uv run python examples/wayfinder_cli.py
```

Interact with the AI assistant directly from your terminal.

## Generate Human Evaluation Dataset

```bash
uv run python examples/human_evaluation/generate_responses.py
```

This generates representative evaluation samples containing:

- User query
- Expected behavior
- Assistant response
- Retrieved tool outputs

These samples can then be reviewed using the Human Evaluation workflow.

## Run Rule-Based Evaluation

```bash
uv run python examples/rule_based_evaluation/local_evaluation.py
```

## Run LangSmith Evaluation

```bash
uv run python examples/rule_based_evaluation/langsmith_evaluation.py
```
## Run LLM-as-a-Judge Evaluation

```bash
uv run python examples/llm_judge_evaluation/local_evaluation.py
```

## Run LLM-as-a-Judge Evaluation with LangSmith

```bash
uv run python examples/llm_judge_evaluation/langsmith_evaluation.py
```

## Run Online Evaluation

First, interact with Wayfinder to generate traced user interactions:

```bash
uv run python examples/wayfinder_cli.py
```

Then run the online evaluator:

```bash
uv run python examples/online_evaluation/evaluate_recent_runs.py
```


The evaluator processes recent Wayfinder interactions captured in LangSmith and attaches automated quality scores and explanations back to each trace.

Explicit user feedback collected through the CLI is also attached to the corresponding [**LangSmith trace**](https://smith.langchain.com).

## Run an Evaluation Experiment

Run the focused experiment-comparison dataset against the current version of Wayfinder:

```bash
uv run python examples/experiment_comparison/compare_experiments.py \
  --dataset-name wayfinder_experiment_comparison \
  --prefix wayfinder-experiment \
  --repetitions 5
```

The runner evaluates the same examples repeatedly and records the results as a LangSmith experiment. Run it against different application versions to compare behavior using the same dataset and evaluator.

# AI Engineering Fundamentals

Wayfinder was built alongside the **AI Engineering Fundamentals — AI Evaluation** article series.

Each article introduces an AI evaluation concept, while this repository provides the runnable implementation.

## Foundations

- ✅ [Part 1 — Software Tests vs AI Evals](https://ai.plainenglish.io/software-tests-vs-ai-evals-why-ai-applications-need-a-different-way-of-testing-205b6ae197fb?sharedUserId=divakar.ungatla)
- ✅ [Part 2 — Understanding AI Evaluation](https://medium.com/ai-in-plain-english/understanding-ai-evaluation-a-practical-framework-for-building-reliable-ai-systems-99922388c7b4?sharedUserId=divakar.ungatla)

## Evaluation Techniques

- ✅ [Part 3 — Rule-Based Evaluation](https://medium.com/towards-artificial-intelligence/rule-based-evaluation-building-a-production-ready-ai-evaluation-pipeline-ee6ada3180b8?sharedUserId=divakar.ungatla)
- ✅ [Part 4 — Human Evaluation](https://pub.towardsai.net/human-evaluation-building-reusable-evaluation-datasets-for-ai-applications-54f6d93fd2db?sharedUserId=divakar.ungatla)
- ✅ [Part 5 — LLM-as-a-Judge](https://medium.com/towards-artificial-intelligence/llm-as-a-judge-building-automated-evaluation-pipelines-for-ai-applications-8680a412a1bd?sharedUserId=divakar.ungatla)
- ✅ [Part 6 — Online Evaluation](https://medium.com/towards-artificial-intelligence/online-evaluation-building-ai-evaluation-pipelines-for-real-user-interactions-a25081a8f390?sharedUserId=divakar.ungatla)
- ✅ [Part 7 — Comparing Evaluation Experiments](https://medium.com/towards-artificial-intelligence/comparing-ai-evaluation-experiments-measuring-the-impact-of-changes-to-ai-applications-e57078deed7f?sharedUserId=divakar.ungatla)

# Releases

Each GitHub release captures a reproducible milestone in Wayfinder's evolution.

Earlier releases correspond to the implementation developed in each article. For Part 7, `v0.6.0` provides the baseline used for the experiment comparison, while `main` contains the completed candidate implementation.

| Milestone | Release |
|-----------|---------|
| Basic Flight Search | [v0.1.0](https://github.com/DivakarUngatla/wayfinder/tree/v0.1.0) |
| Rule-Based Evaluation | [v0.2.2](https://github.com/DivakarUngatla/wayfinder/tree/v0.2.2) |
| Human Evaluation | [v0.3.0](https://github.com/DivakarUngatla/wayfinder/tree/v0.3.0) |
| LLM-as-a-Judge | [v0.4.0](https://github.com/DivakarUngatla/wayfinder/tree/v0.4.0) |
| Online Evaluation | [v0.5.0](https://github.com/DivakarUngatla/wayfinder/tree/v0.5.0) |
| Experiment Comparison | [v0.6.0](https://github.com/DivakarUngatla/wayfinder/tree/v0.6.0) |

# Contributing

Contributions, ideas, bug reports, and suggestions are always welcome.

If you'd like to improve Wayfinder or discuss AI evaluation techniques, feel free to open an issue or submit a pull request.

# License

This project is licensed under the MIT License.