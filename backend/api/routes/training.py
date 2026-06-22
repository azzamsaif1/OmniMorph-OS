"""Training API routes — curriculum generation, model training, MoE routing."""

from fastapi import APIRouter
from pydantic import BaseModel

router = APIRouter(prefix="/api/training-ops", tags=["training"])


class CurriculumRequest(BaseModel):
    agent_type: str  # security|trading|software
    current_accuracy: float = 0.5
    target_accuracy: float = 0.9


class TrainingDataRequest(BaseModel):
    agent_type: str
    difficulty: int = 1
    count: int = 100


class TrainRequest(BaseModel):
    agent_type: str
    training_data: list[dict] = []
    base_model: str = "llama-3-8b"


class RouteRequest(BaseModel):
    query: str


@router.post("/curriculum")
async def generate_curriculum(req: CurriculumRequest):
    """Generate training curriculum for a specialist agent (ALAS-style)."""
    from backend.training.curriculum_generator import CurriculumGenerator
    gen = CurriculumGenerator()
    return await gen.generate_curriculum(req.agent_type, req.current_accuracy, req.target_accuracy)


@router.post("/data/generate")
async def generate_training_data(req: TrainingDataRequest):
    """Generate training data for a specific difficulty level."""
    from backend.training.curriculum_generator import CurriculumGenerator
    gen = CurriculumGenerator()
    return await gen.generate_training_data(req.agent_type, req.difficulty, req.count)


@router.post("/train")
async def train_model(req: TrainRequest):
    """Execute a training run (simulation — actual training requires GPU)."""
    from backend.training.trainer import ModelTrainer
    trainer = ModelTrainer()
    config_result = await trainer.prepare_training_config(req.agent_type, req.base_model)
    return await trainer.train_model(req.agent_type, req.training_data, config_result["config"])


@router.post("/route")
async def route_query(req: RouteRequest):
    """Route a query to the best specialist using MoE."""
    from backend.training.moe_router import MoERouter
    router_instance = MoERouter()
    return await router_instance.route_with_ai(req.query)


@router.get("/config/{agent_type}")
async def get_training_config(agent_type: str):
    """Get training configuration for an agent type."""
    from backend.training.trainer import ModelTrainer
    trainer = ModelTrainer()
    return await trainer.prepare_training_config(agent_type)


@router.get("/stats")
async def training_stats():
    """Get training system statistics."""
    from backend.training.trainer import ModelTrainer
    from backend.training.moe_router import MoERouter
    trainer = ModelTrainer()
    moe = MoERouter()
    return {
        "trainer": trainer.get_training_history(),
        "router": moe.get_routing_stats(),
    }
