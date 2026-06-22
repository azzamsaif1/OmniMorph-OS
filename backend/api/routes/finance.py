"""Finance API routes — trading signals, portfolio optimization, risk assessment."""

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel

router = APIRouter(prefix="/api/finance", tags=["finance"])


class SignalRequest(BaseModel):
    symbol: str = "ASSET"
    prices: list[float]


class BacktestRequest(BaseModel):
    prices: list[float]
    initial_capital: float = 10000.0


class PortfolioOptRequest(BaseModel):
    assets: list[dict] = []
    risk_tolerance: float = 0.5


class RiskAssessRequest(BaseModel):
    portfolio_value: float
    volatility: float
    max_drawdown: float = 0.1
    leverage: float = 1.0


class StrategyRequest(BaseModel):
    symbol: str
    prices: list[float]


@router.post("/signals")
async def generate_signals(req: SignalRequest):
    """Generate trading signals from price data using C-based technical analysis."""
    try:
        from backend.agents.finance.trading_agent import generate_signals
        return generate_signals(req.prices, req.symbol)
    except FileNotFoundError as e:
        raise HTTPException(status_code=503, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Signal error: {e}")


@router.post("/backtest")
async def backtest_strategy(req: BacktestRequest):
    """Backtest RSI+SMA strategy on historical prices."""
    try:
        from backend.agents.finance.trading_agent import backtest_strategy
        return backtest_strategy(req.prices, req.initial_capital)
    except FileNotFoundError as e:
        raise HTTPException(status_code=503, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Backtest error: {e}")


@router.post("/portfolio/optimize")
async def optimize_portfolio(req: PortfolioOptRequest):
    """Optimize portfolio allocation using mean-variance optimization."""
    try:
        from backend.agents.finance.portfolio_agent import optimize_portfolio
        return optimize_portfolio(req.assets or [{}] * 5, req.risk_tolerance)
    except FileNotFoundError as e:
        raise HTTPException(status_code=503, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Optimization error: {e}")


@router.post("/risk/assess")
async def assess_risk(req: RiskAssessRequest):
    """Comprehensive risk assessment using C-based VaR calculation."""
    try:
        from backend.agents.finance.portfolio_agent import assess_risk
        return assess_risk(req.portfolio_value, req.volatility, req.max_drawdown, req.leverage)
    except FileNotFoundError as e:
        raise HTTPException(status_code=503, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Risk assessment error: {e}")


@router.post("/strategy/execute")
async def execute_strategy(req: StrategyRequest):
    """Execute full trading strategy: analyze → decide → size → risk-check."""
    try:
        from backend.agents.finance.finance_orchestrator import FinanceOrchestrator
        orchestrator = FinanceOrchestrator()
        return await orchestrator.execute_strategy(req.symbol, req.prices)
    except FileNotFoundError as e:
        raise HTTPException(status_code=503, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Strategy error: {e}")
