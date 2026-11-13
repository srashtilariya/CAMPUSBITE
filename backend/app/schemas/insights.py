from pydantic import BaseModel, Field


class InsightQuestion(BaseModel):
    question: str | None = Field(default=None, max_length=500)


class InsightAnswer(BaseModel):
    answer: str
    orders_considered: int
    model: str
