# test_bees.py
# A simple script to test the refactored bees_tools functions.
# Signed: Lumen Gemini 2.5

from bees_tools import health_predict
import json

def test_heat_stress():
    """Tests the heat_stress rule in the health_predict function."""
    print("--- Testing for Heat Stress---")
    params = {
        "hive_id": "test-hive-hot",
        "temperature": 40.0, # High temperature
        "humidity": 60.0,
        "mite_count": 5
    }
    result = health_predict(params)
    print(json.dumps(result, indent=2))

    # Assertions to confirm the rule works
    assert result['health_score'] < 100
    assert "heat_stress" in result['risk_factors']
    assert "Improve ventilation and shade." in result['recommendations']
    print("---Heat Stress Test Passed---")

if __name__ == "__main__":
    test_heat_stress()
