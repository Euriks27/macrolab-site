import pytest
from macrolab.dynamics import simulate_debt_trajectory

def test_debt_trajectory_stable():
    """Test debt trajectory with stable parameters"""
    trajectory = simulate_debt_trajectory(
        years=5,
        initial_debt=60,
        interest_rate=0.05,
        growth_rate=0.03,
        primary_balance=2.0
    )
    assert len(trajectory) == 5
    assert trajectory[0] == 60
    # With these parameters, debt should increase moderately
    assert trajectory[-1] > trajectory[0]

def test_debt_trajectory_unsustainable():
    """Test debt trajectory with unsustainable parameters"""
    trajectory = simulate_debt_trajectory(
        years=10,
        initial_debt=70,
        interest_rate=0.08,
        growth_rate=0.01,
        primary_balance=0.5
    )
    assert len(trajectory) == 10
    # With high interest rate and low growth, debt should escalate
    assert trajectory[-1] > trajectory[0] * 1.5