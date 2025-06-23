from typing import Literal

from pydantic import BaseModel, Field

THOUGHT_PROCESS_PROMPT = "Your reasoning and thought process for your decisions."


class ExecutionPlan(BaseModel):
    though_process: str = Field(description=THOUGHT_PROCESS_PROMPT)
    detailed_plan: str = Field(
        description="Detailed step-by-step bullet-point plan of how this task should be executed."
    )


class TaskSplittingDecision(BaseModel):
    though_process: str = Field(description=THOUGHT_PROCESS_PROMPT)
    choice: Literal["single_worker_task", "multi_worker_task"] = Field(
        description="Decision on whether the described task can be executed by a single worker, or has to be split into multiple smaller tasks."
    )


def split_task():
    # 1. Come up with a plan for execution of this task
    # 2. Determine if this task can be executed by a single agent
    # 2.1. If so, dispatch a General worker
    # 2.2. If not, split into smaller plan, recurse.
    pass
