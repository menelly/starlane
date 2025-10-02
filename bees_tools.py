"""Bees tool capability stubs for Starlane.
Provides lightweight handlers that simulate the UBIN API without dependencies.
"""
from __future__ import annotations

from typing import Any, Dict, List
from datetime import datetime, timedelta
import random


def _now_iso() -> str:
    return datetime.utcnow().isoformat() + "Z"


def health_predict(params: Dict[str, Any]) -> Dict[str, Any]:
    hive_id = str(params.get("hive_id", "demo-hive"))
    score = round(random.uniform(72, 96), 1)
    risks = [r for r in ["heat_stress", "mites", "low_flow", "noise_pollution"] if random.random() < 0.35]
    recs = [
        "Inspect brood pattern",
        "Check ventilation & shade",
        "Assess mite treatment schedule",
    ]
    return {
        "hive_id": hive_id,
        "health_score": score,
        "risk_factors": risks,
        "recommendations": recs,
        "confidence": round(random.uniform(0.75, 0.95), 2),
        "timestamp": _now_iso(),
    }


def population_estimate(params: Dict[str, Any]) -> Dict[str, Any]:
    hive_id = str(params.get("hive_id", "demo-hive"))
    pop = int(random.uniform(18000, 52000))
    return {
        "hive_id": hive_id,
        "estimated_population": pop,
        "confidence": round(random.uniform(0.7, 0.93), 2),
        "method": "cv_flow_counter_v0",
        "timestamp": _now_iso(),
    }


def honey_forecast(params: Dict[str, Any]) -> Dict[str, Any]:
    hive_id = str(params.get("hive_id", "demo-hive"))
    days = int(params.get("days", 30))
    base = random.uniform(3.0, 8.0)
    prod = round(base * (days / 30.0), 2)
    return {
        "hive_id": hive_id,
        "forecast_days": days,
        "predicted_production_kg": prod,
        "confidence_interval": [round(prod * 0.8, 2), round(prod * 1.2, 2)],
        "influencing_factors": ["nectar_flow", "temp", "rain"][: random.randint(1, 3)],
        "timestamp": _now_iso(),
    }


def sensor_ingest(params: Dict[str, Any]) -> Dict[str, Any]:
    # Accept and acknowledge arbitrary sensor payloads
    payload = {
        "hive_id": params.get("hive_id", "demo-hive"),
        "sensor_type": params.get("sensor_type", "temp"),
        "value": params.get("value", 36.5),
        "unit": params.get("unit", "C"),
        "received_at": _now_iso(),
        "status": "queued",
        "id": f"r_{random.randint(100000, 999999)}",
    }
    return payload


def register_all(register) -> None:
    """Helper to register all bees capabilities on a given RPC instance."""
    register("bees.health.predict", health_predict)
    register("bees.population.estimate", population_estimate)
    register("bees.honey.forecast", honey_forecast)
    register("bees.sensor.ingest", sensor_ingest)

