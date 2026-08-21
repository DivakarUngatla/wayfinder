from pydantic import BaseModel, Field

class CriterionScore(BaseModel):
    """Represents the score and explanation for a single evaluation criterion."""
    criterion: str = Field(description="The criterion being evaluated.")
    score: int = Field(ge=1, le= 5, description="The score for the criterion on a scale of 1 to 5.")
    explanation: str = Field(description="Explanation for the score.")



class JudgeResult(BaseModel):
    """Result of evaluating an agent response."""
    criteria_scores : list[CriterionScore] = Field(description="List of evaluation criteria with their scores.")
    overall_score: int = Field(ge=1, le= 5, description="Overall score for the agent response.")
    overall_explanation: str = Field(description="Natural language explanation for the overall score.")
