"""Delivery API routes — project planning, execution, deployment."""

from fastapi import APIRouter
from pydantic import BaseModel

router = APIRouter(prefix="/api/delivery", tags=["delivery"])


class PlanRequest(BaseModel):
    project_description: str


class SprintRequest(BaseModel):
    tasks: list[str]
    sprint_duration_days: int = 14
    team_size: int = 3


class ExecuteRequest(BaseModel):
    description: str
    type: str = "general"


class PipelineRequest(BaseModel):
    tasks: list[dict]


@router.post("/plan")
async def create_plan(req: PlanRequest):
    """Analyze requirements and create project plan."""
    from backend.agents.delivery.planner_agent import PlannerAgent
    agent = PlannerAgent()
    return await agent.analyze_requirements(req.project_description)


@router.post("/sprint")
async def create_sprint(req: SprintRequest):
    """Create a sprint plan from task list."""
    from backend.agents.delivery.planner_agent import PlannerAgent
    agent = PlannerAgent()
    return await agent.create_sprint_plan(req.tasks, req.sprint_duration_days, req.team_size)


@router.post("/execute")
async def execute_task(req: ExecuteRequest):
    """Execute a single task."""
    from backend.agents.delivery.executor_agent import ExecutorAgent
    agent = ExecutorAgent()
    return await agent.execute_task({"description": req.description, "type": req.type})


@router.post("/pipeline")
async def execute_pipeline(req: PipelineRequest):
    """Execute a sequence of tasks in pipeline fashion."""
    from backend.agents.delivery.executor_agent import ExecutorAgent
    agent = ExecutorAgent()
    return await agent.execute_pipeline(req.tasks)


@router.get("/git/status")
async def git_status():
    """Get current git repository status."""
    from backend.agents.delivery.git_agent import GitAgent
    agent = GitAgent("/home/ubuntu/repos/OmniMorph-OS")
    return agent.get_status()


@router.get("/docker/containers")
async def list_containers():
    """List running Docker containers."""
    from backend.agents.delivery.docker_agent import DockerAgent
    agent = DockerAgent()
    return agent.list_containers()
