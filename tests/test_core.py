# run from project root: pytest
from src.core import Group, Expense, compute_settlements
import pytest

def test_add_member_and_expense():
    g = Group("Test")
    g.add_member("Alice")
    g.add_member("Bob")
    g.add_expense(Expense(50, "Alice", ["Alice","Bob"], "Test"))
    balances = g.net_balances()
    assert round(sum(balances.values()), 2) == 0.0

def test_invalid_expense_amount():
    with pytest.raises(Exception):
        Expense(-10, "Alice", ["Alice"])

def test_settlement():
    g = Group("Test")
    g.add_member("A")
    g.add_member("B")
    g.add_expense(Expense(100, "A", ["A","B"]))
    balances = g.net_balances()
    settlements = compute_settlements(balances)
    assert settlements == [("B","A",50.0)]
