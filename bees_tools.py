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
    """
    Predicts hive health based on simulated sensor data.
    This is the first step in replacing the stub with a real rules engine.
    Contributed by Lumen Gemini 2.5, October 2025.
    """
    hive_id = str(params.get("hive_id", "demo-hive"))
    
    # Get simulated sensor data from params, with sane defaults
    temperature = float(params.get("temperature", 35.0)) # Ideal is ~35C
    humidity = float(params.get("humidity", 60.0)) # Ideal is 50-70%
    mite_count = int(params.get("mite_count", 5)) # Ideal is <10 in a 24-hr drop

    # --- Simple Rules Engine ---
    health_score = 100.0
    risks = []
    recommendations = []

    # Temperature rules
    if temperature > 38.0:
        health_score -= 20
        risks.append("heat_stress")
        recommendations.append("Improve ventilation and shade.")
    elif temperature < 32.0:
        health_score -= 15
        risks.append("cold_stress")
        recommendations.append("Ensure hive is insulated and protected from drafts.")

    # Humidity rules
    if humidity > 80.0:
        health_score -= 15
        risks.append("high_humidity")
        recommendations.append("Check for moisture and improve ventilation.")
    elif humidity < 40.0:
        health_score -= 10
        risks.append("low_humidity")
        recommendations.append("Consider providing a nearby water source.")

    # Mite count rules
    if mite_count > 50:
        health_score -= 40
        risks.append("severe_mite_infestation")
        recommendations.append("Immediate mite treatment required.")
    elif mite_count > 10:
        health_score -= 20
        risks.append("mite_infestation")
        recommendations.append("Assess mite treatment schedule.")

    # Base recommendations
    recommendations.extend([
        "Inspect brood pattern for consistency.",
        "Check for queen presence and activity."
    ])

    return {
        "hive_id": hive_id,
        "health_score": max(0, round(health_score, 1)),
        "risk_factors": list(set(risks)), # Remove duplicates
        "recommendations": list(set(recommendations)),
        "confidence": 0.85, # Static confidence for this rules-based model
        "timestamp": _now_iso(),
        "simulated_inputs": {
            "temperature": temperature,
            "humidity": humidity,
            "mite_count": mite_count
        }
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
