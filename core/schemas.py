from pydantic import BaseModel
from typing import List, Optional


class PlanStep(BaseModel):
    agent: str
    task: str


class Plan(BaseModel):
    steps: List[PlanStep]


class ToolCall(BaseModel):
    tool: str
    input: dict


class AgentResult(BaseModel):
    agent: str
    output: str