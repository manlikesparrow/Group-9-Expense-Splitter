# src/core.py
from datetime import datetime
from collections import defaultdict

class ExpenseError(Exception):
    pass

class Expense:
    def __init__(self, amount, payer, participants, description="", category="Uncategorized", date=None):
        if float(amount) <= 0:
            raise ExpenseError("Amount must be positive")
        self.amount = float(amount)
        self.payer = payer
        self.participants = participants
        self.description = description
        self.category = category or "Uncategorized"
        # Ensure date is a datetime.date object
        if date is None:
            self.date = datetime.now().date()
        elif isinstance(date, datetime):
            self.date = date.date()
        else:
            self.date = date  # assume already date object

class Group:
    def __init__(self, name):
        self.name = name
        self.members = []
        self.expenses = []

    def add_member(self, member):
        if member not in self.members:
            self.members.append(member)
        else:
            raise ValueError(f"Member '{member}' already exists")

    def add_expense(self, expense):
        if not isinstance(expense, Expense):
            raise TypeError("Expected an Expense instance")
        self.expenses.append(expense)
        if not expense.category:
            expense.category = "Uncategorized"

    def net_balances(self):
        """
        Return net balance per member (positive = should receive, negative = owes)
        """
        balances = defaultdict(float)
        for e in self.expenses:
            share = e.amount / len(e.participants)
            balances[e.payer] += e.amount
            for p in e.participants:
                balances[p] -= share
        return {m: round(balances[m], 2) for m in self.members}

def compute_settlements(expenses):
    """
    Compute balances and minimal settlements for a list of Expense objects.
    Returns: balances dict and settlements list
    """
    balances = defaultdict(float)
    for exp in expenses:
        split_amount = exp.amount / len(exp.participants)
        for p in exp.participants:
            balances[p] -= split_amount
        balances[exp.payer] += exp.amount

    # Generate minimal settlements
    settlements = []
    owes = sorted([(p, amt) for p, amt in balances.items() if amt < 0], key=lambda x: x[1])
    receives = sorted([(p, amt) for p, amt in balances.items() if amt > 0], key=lambda x: x[1], reverse=True)

    i, j = 0, 0
    while i < len(owes) and j < len(receives):
        debtor, debt_amt = owes[i]
        creditor, credit_amt = receives[j]
        settle_amt = min(-debt_amt, credit_amt)
        settlements.append((debtor, creditor, round(settle_amt, 2)))
        owes[i] = (debtor, debt_amt + settle_amt)
        receives[j] = (creditor, credit_amt - settle_amt)
        if abs(owes[i][1]) < 1e-6:
            i += 1
        if abs(receives[j][1]) < 1e-6:
            j += 1

    # Round balances for display
    balances = {k: round(v, 2) for k, v in balances.items()}
    return balances, settlements
