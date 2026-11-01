"""Delete the demo database and re-create the synthetic data.  Usage (from backend/):  python -m scripts.reset_demo"""
from app import seed

seed.reset()
print("Data reset: every branch of every school has 2 teachers (T10001...) and 18 Class 8 students (S10001...). PIN 1234. See APPLY notes for the list.")
