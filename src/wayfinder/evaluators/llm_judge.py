"""LLM-as-a-Judge evaluator for Wayfinder.

Uses an LLM to evaluate an assistant response against a set of explicit
evaluation criteria and a scoring rubric, returning structured scores and
explanations for each criterion alongside an overall assessment.
"""

import json

import openai

from typing import Any

from wayfinder.evaluators.criteria import CRITERIA
from wayfinder.models.judge_result import JudgeResult

JUDGE_MODEL = "gpt-4o"

_SYSTEM_PROMPT = """\
You are an expert evaluator assessing the quality of an AI assistant response.

You will be given:
- The user's original query.
- The expected behavior: a description of what a good assistant response should do for this query.
- The assistant's actual response.
- The context available to the application before generating the response.

Your task is to evaluate the assistant's response against each of the following criteria.

Evaluation criteria and rubric:
{criteria_block}

Instructions:
- "Expected behavior" describes what the application was expected to do for this sample.
  It is not a model answer. Use it to understand the intent of the query.
- Evaluate the response against each criterion independently.
- When evaluating Groundedness, cross-reference the response against the supplied context.
- Do not invent facts that are not present in the supplied context.
- Score every criterion from 1 to 5 using the rubric above.
- Provide a concise explanation for every criterion score.
- Provide an overall score from 1 to 5 that reflects your holistic judgment.
  Do not calculate the overall score as an average of the criteria scores.
- Provide a concise overall explanation.
"""

_USER_PROMPT = """\
User query:
{query}

Expected behavior:
{expected_behavior}

Assistant response:
{response}

Context:
{context_json}
"""


def _build_criteria_block() -> str:
    """Render CRITERIA as a numbered list for the system prompt."""
    lines = []
    for i, criterion in enumerate(CRITERIA, start=1):
        lines.append(f"{i}. {criterion.name}")
        lines.append(f"   Definition: {criterion.definition}")
        lines.append(f"   Rubric: {criterion.rubric}")
    return "\n".join(lines)


# Built once at module load; CRITERIA is a module-level constant.
_CRITERIA_BLOCK = _build_criteria_block()


class LLMJudge:
    """Evaluates an assistant response using an LLM as the judge.

    Uses structured output (client.beta.chat.completions.parse) to return
    a JudgeResult containing a score and explanation for each criterion
    plus an overall score and explanation.
    """

    def __init__(self, client: openai.OpenAI) -> None:
        """Initialise the judge with an OpenAI client."""
        self._client = client

    def evaluate(
        self,
        query: str,
        expected_behavior: str,
        response: str,
        context: Any,
    ) -> JudgeResult:
        """Evaluate an assistant response and return structured scores.

        Args:
            query:              The original user query.
            expected_behavior:  High-level description of what the assistant
                                should have done for this query.
            response:           The assistant's natural-language response.
            context:            Generic supporting information available to the
                                application before the response was generated.

        Returns:
            A JudgeResult with a score and explanation for each criterion
            and an overall assessment.
        """
        def default_serializer(obj: Any) -> Any:
            if hasattr(obj, "model_dump"):
                return obj.model_dump(mode="json")
            return str(obj)

        context_json = json.dumps(
            context,
            default=default_serializer,
            indent=2,
        )

        result = self._client.beta.chat.completions.parse(
            model=JUDGE_MODEL,
            messages=[
                {
                    "role": "system",
                    "content": _SYSTEM_PROMPT.format(
                        criteria_block=_CRITERIA_BLOCK
                    ),
                },
                {
                    "role": "user",
                    "content": _USER_PROMPT.format(
                        query=query,
                        expected_behavior=expected_behavior,
                        response=response,
                        context_json=context_json,
                    ),
                },
            ],
            response_format=JudgeResult,
        )

        parsed = result.choices[0].message.parsed

        if parsed is None:
            raise ValueError("LLM judge returned no structured output.")

        return parsed
