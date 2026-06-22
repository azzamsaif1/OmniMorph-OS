"""Finance orchestrator — coordinates trading, portfolio, and risk agents."""

import time
from typing import Any

from backend.agents.finance.trading_agent import (
    generate_signals,
    kelly_position_size,
    backtest_strategy,
)
from backend.agents.finance.portfolio_agent import (
    optimize_portfolio,
    calculate_var,
    assess_risk,
)


class FinanceOrchestrator:
    """Orchestrates financial agents: Market Analysis → Signal → Position → Risk."""

    def __init__(self, initial_capital: float = 100000.0):
        self.capital = initial_capital
        self.positions: list[dict] = []
        self.trade_history: list[dict] = []
        self.evolution_log: list[dict] = []

    async def analyze_market(
        self, symbol: str, prices: list[float]
    ) -> dict[str, Any]:
        """Full market analysis pipeline for a single asset."""
        # Generate technical signals
        signals = generate_signals(prices, symbol)

        # Backtest strategy on historical data
        backtest = backtest_strategy(prices, self.capital)

        # Calculate position size
        win_rate = backtest.get("win_rate", 50.0) / 100.0
        avg_win = max(prices) - sum(prices) / len(prices) if prices else 0
        avg_loss = sum(prices) / len(prices) - min(prices) if prices else 1
        position_size = kelly_position_size(
            win_rate, abs(avg_win), abs(avg_loss) + 0.01, self.capital
        )

        # Risk assessment
        volatility = self._calculate_volatility(prices)
        risk = assess_risk(self.capital, volatility)

        return {
            "symbol": symbol,
            "signal": signals,
            "backtest": backtest,
            "recommended_position_size": position_size,
            "risk_assessment": risk,
            "timestamp": int(time.time()),
        }

    async def optimize_allocation(
        self, assets: list[dict], risk_tolerance: float = 0.5
    ) -> dict[str, Any]:
        """Optimize portfolio allocation across multiple assets."""
        allocation = optimize_portfolio(assets, risk_tolerance)

        # Calculate portfolio VaR
        portfolio_value = sum(a.get("value", 0) for a in assets) or self.capital
        avg_vol = sum(a.get("volatility", 0.2) for a in assets) / max(len(assets), 1)
        var_95 = calculate_var(portfolio_value, avg_vol, 0.95, 1)

        allocation["portfolio_var_95"] = var_95
        allocation["total_portfolio_value"] = portfolio_value

        return allocation

    async def execute_strategy(
        self, symbol: str, prices: list[float]
    ) -> dict[str, Any]:
        """Execute full trading strategy: analyze → decide → size → risk-check."""
        analysis = await self.analyze_market(symbol, prices)

        signal = analysis["signal"].get("signal", "HOLD")
        confidence = analysis["signal"].get("confidence", 0.0)

        decision = {
            "symbol": symbol,
            "action": signal,
            "confidence": confidence,
            "position_size": analysis["recommended_position_size"],
            "risk_level": analysis["risk_assessment"].get("risk_level", "unknown"),
            "executed": False,
            "reason": "",
        }

        # Only execute if confidence is high enough and risk is acceptable
        risk_score = analysis["risk_assessment"].get("risk_score", 100)
        if confidence >= 0.6 and risk_score < 75:
            decision["executed"] = True
            decision["reason"] = f"High confidence ({confidence:.0%}) with acceptable risk ({risk_score:.0f}/100)"
            self.trade_history.append(decision)
        else:
            decision["reason"] = f"Skipped: confidence={confidence:.0%}, risk={risk_score:.0f}/100"

        return decision

    def _calculate_volatility(self, prices: list[float]) -> float:
        """Calculate annualized volatility from price series."""
        if len(prices) < 2:
            return 0.2
        returns = [
            (prices[i] - prices[i - 1]) / prices[i - 1]
            for i in range(1, len(prices))
        ]
        mean_ret = sum(returns) / len(returns)
        variance = sum((r - mean_ret) ** 2 for r in returns) / len(returns)
        daily_vol = variance ** 0.5
        return daily_vol * (252 ** 0.5)  # Annualize

    def get_performance_summary(self) -> dict[str, Any]:
        """Get overall trading performance summary."""
        executed = [t for t in self.trade_history if t.get("executed")]
        return {
            "total_trades": len(executed),
            "capital": self.capital,
            "active_positions": len(self.positions),
            "evolution_cycles": len(self.evolution_log),
        }
