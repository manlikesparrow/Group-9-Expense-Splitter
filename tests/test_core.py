# run from project root: pytest
import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from src.core import Group, Expense, compute_settlements, ExpenseError
import pytest

def test_add_member_and_expense():
    g = Group("Test")
    g.add_member("Alice")
    g.add_member("Bob")
    g.add_expense(Expense(50, "Alice", ["Alice","Bob"], "Test"))
    balances = g.net_balances()
    # Total sum of balances should be 0
    assert round(sum(balances.values()), 2) == 0.0
    # Check individual balances
    assert balances["Alice"] == 25.0
    assert balances["Bob"] == -25.0

def test_invalid_expense_amount():
    with pytest.raises(ExpenseError):
        Expense(-10, "Alice", ["Alice"])

def test_settlement():
    g = Group("Test")
    g.add_member("A")
    g.add_member("B")
    exp = Expense(100, "A", ["A","B"])
    g.add_expense(exp)
    balances, settlements = compute_settlements(g.expenses)
    # Balances
    assert balances["A"] == 50.0
    assert balances["B"] == -50.0
    # Settlements
    assert settlements == [("B","A",50.0)]
