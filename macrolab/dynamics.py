import numpy as np
import pandas as pd

def simulate_debt_trajectory(years, initial_debt, interest_rate, growth_rate, primary_balance):
    """Calculates the debt-to-GDP trajectory over time."""
    trajectory = [initial_debt]
    for _ in range(1, years):
        # Debt dynamics formula: D_t = D_{t-1} * (1+r)/(1+g) - PB
        next_debt = trajectory[-1] * ((1 + interest_rate) / (1 + growth_rate)) - primary_balance
        trajectory.append(next_debt)
    return trajectory