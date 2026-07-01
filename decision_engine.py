# -*- coding: utf-8 -*-
from __future__ import annotations

from typing import Dict, Any
from config import BASE_WEIGHTS, INITIAL_POSITIONS


def classify_market(data: Dict[str, Any]) -> Dict[str, Any]:
    stocks = data.get("stocks", {})
    market = data.get("market", {})
    changes = [v.get("涨跌幅%") for v in stocks.values() if v.get("涨跌幅%") is not None]
    amps = [v.get("振幅%") for v in stocks.values() if v.get("振幅%") is not None]
    avg_change = sum(changes) / len(changes) if changes else 0
    avg_amp = sum(amps) / len(amps) if amps else 0
    cyb = market.get("创业板%") or 0
    sh = market.get("上证%") or 0

    # 先用简单规则，后续用历史样本修正。
    if avg_change > 4 and avg_amp < 7:
        regime = "强趋势上涨"
        t0_participation = 0.30
        risk = "卖飞风险高"
    elif avg_amp >= 7 and avg_change > -2:
        regime = "高波动/放量震荡"
        t0_participation = 1.00
        risk = "适合T0，但要防急拉卖飞"
    elif avg_change < -3 or (cyb < -1.5 and avg_change < 0):
        regime = "弱势/下跌"
        t0_participation = 0.20
        risk = "保守，只做低比例"
    elif abs(avg_change) <= 2 and avg_amp >= 4:
        regime = "震荡"
        t0_participation = 0.80
        risk = "较适合T0"
    else:
        regime = "普通行情"
        t0_participation = 0.60
        risk = "中性"

    market_score = round(max(1, min(5, 3 + avg_change / 2 + avg_amp / 5)), 1)
    return {
        "regime": regime,
        "t0_participation": t0_participation,
        "risk": risk,
        "avg_stock_change": round(avg_change, 2),
        "avg_stock_amplitude": round(avg_amp, 2),
        "market_score": market_score,
    }


def provider_weights(regime: str) -> Dict[str, float]:
    if regime == "强趋势上涨":
        return {"非凸": 0.50, "跃然": 0.20, "卡方": 0.20, "皓兴": 0.10}
    if regime == "高波动/放量震荡":
        return {"非凸": 0.35, "跃然": 0.35, "卡方": 0.20, "皓兴": 0.10}
    if regime == "弱势/下跌":
        return {"非凸": 0.45, "卡方": 0.35, "跃然": 0.10, "皓兴": 0.10}
    if regime == "震荡":
        return {"卡方": 0.35, "非凸": 0.30, "跃然": 0.25, "皓兴": 0.10}
    return BASE_WEIGHTS.copy()


def recommend(data: Dict[str, Any]) -> Dict[str, Any]:
    cls = classify_market(data)
    weights = provider_weights(cls["regime"])
    participation = cls["t0_participation"]

    # 总T0参与资金 = 持仓市值合计 * 参与度
    positions = INITIAL_POSITIONS.copy()
    total_position = sum(positions.values())
    active_amount = total_position * participation

    provider_amounts = {k: round(active_amount * v, 0) for k, v in weights.items()}

    # 股票分配：第一版按持仓占比分配；后续加入每只股票适合度。
    stock_amounts = {k: round(v * participation, 0) for k, v in positions.items()}

    return {
        "classification": cls,
        "provider_weights": weights,
        "provider_amounts": provider_amounts,
        "stock_amounts": stock_amounts,
        "total_position": total_position,
        "active_amount": round(active_amount, 0),
    }
