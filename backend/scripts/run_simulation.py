"""Run the 50-student validation simulation and save the real output.  Usage (from backend/):  python -m scripts.run_simulation"""
import json
import os

from app import sim

out = sim.validate(n=50, seed=2026)
path = os.path.join(os.path.dirname(__file__), "..", "data", "validation.json")
os.makedirs(os.path.dirname(path), exist_ok=True)
json.dump(out, open(path, "w"), indent=2)
print(json.dumps(out, indent=2))
