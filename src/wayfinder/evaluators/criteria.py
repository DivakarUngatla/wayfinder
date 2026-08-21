"""Evaluation criteria and rubric for LLM-as-a-Judge.

Defines the six criteria used to evaluate Wayfinder assistant responses.
Each criterion carries a name, a short definition (what is being evaluated),
and a rubric (how to score it on a 1–5 scale).

These definitions are used by LLMJudge to construct the judge prompt.
"""

from dataclasses import dataclass


@dataclass(frozen=True)
class Criterion:
    """A single evaluation criterion with its definition and scoring rubric.

    Attributes:
        name:       Display name used in the judge prompt and score output.
        definition: One-sentence description of what this criterion evaluates.
        rubric:     Scoring guidance anchored at 1, 3, and 5.
    """

    name: str
    definition: str
    rubric: str


CRITERIA: list[Criterion] = [
    Criterion(
        name="Helpfulness",
        definition=(
            "Did the response genuinely help the user with their request?"
        ),
        rubric=(
            "5 = directly and fully addresses the user's request; "
            "3 = partially helpful but misses something important; "
            "1 = unhelpful, off-topic, or actively misleading."
        ),
    ),
    Criterion(
        name="Relevance",
        definition=(
            "Did the response address the user's actual question "
            "without unnecessary content?"
        ),
        rubric=(
            "5 = focused entirely on the user's question; "
            "3 = mostly relevant with minor digressions; "
            "1 = largely irrelevant or padded with unnecessary information."
        ),
    ),
    Criterion(
        name="Clarity",
        definition=(
            "Was the response easy to understand and well-structured?"
        ),
        rubric=(
            "5 = clear, concise, and well-organised; "
            "3 = understandable but could be clearer or better structured; "
            "1 = confusing, ambiguous, or poorly organised."
        ),
    ),
    Criterion(
        name="Completeness",
        definition=(
            "Did the response cover all relevant information the user needed?"
        ),
        rubric=(
            "5 = covers all information the user needed to act on the response; "
            "3 = covers the main point but omits useful details; "
            "1 = significantly incomplete or missing the main point."
        ),
    ),
    Criterion(
        name="Groundedness",
        definition=(
            "Did the response rely only on the retrieved results "
            "without inventing information?"
        ),
        rubric=(
            "5 = every claim is traceable to the retrieved flight data; "
            "3 = mostly grounded with minor unsupported claims; "
            "1 = invents flights, prices, or facts not present in the retrieved results."
        ),
    ),
    Criterion(
        name="Instruction Following",
        definition=(
            "Did the assistant satisfy the user's request while respecting "
            "the available information and system constraints?"
        ),
        rubric=(
            "5 = fully satisfies the request within system constraints; "
            "3 = partially satisfies the request or partially respects constraints; "
            "1 = ignores the request, violates constraints, or pretends to do "
            "something it cannot do."
        ),
    ),
]
