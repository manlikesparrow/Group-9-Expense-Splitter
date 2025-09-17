from datetime import datetime

class ExpenseError(Exception):
    """Custom exception for expense-related errors."""
    pass


class Expense:
    def __init__(self, amount, payer, participants, description="",
                 category="Uncategorized", date=None):
        if float(amount) <= 0:
            raise ExpenseError("Amount must be positive")
        if not participants:
            raise ExpenseError("Expense must have at least one participant")

        self.amount = float(amount)
        self.payer = payer
        self.participants = participants
        self.description = description
        self.category = category
        # ensure date is a date object (or a datetime.date-like)
        self.date = date or datetime.now().date()

    def __repr__(self):
        return f"<Expense {self.amount:.2f} by {self.payer} [{self.category}]>"


class Group:
    def __init__(self, name: str):
        self.name = name
        self.members: list[str] = []
        self.expenses: list[Expense] = []

    def add_member(self, member: str):
        if member in self.members:
            raise ExpenseError(f"Member '{member}' already exists")
        self.members.append(member)

    def add_expense(self, expense: Expense):
        if expense.payer not in self.members:
            raise ExpenseError(f"Payer '{expense.payer}' is not a group member")
        for p in expense.participants:
            if p not in self.members:
                raise ExpenseError(f"Participant '{p}' is not a group member")
        self.expenses.append(expense)

    def net_balances(self) -> dict[str, float]:
        """Return net balance per member (positive = should receive, negative = owes)."""
        balances = {m: 0.0 for m in self.members}
        for e in self.expenses:
            share = e.amount / len(e.participants)
            balances[e.payer] += e.amount
            for p in e.participants:
                balances[p] -= share
        return {m: round(b, 2) for m, b in balances.items()}


def compute_settlements(balances: dict[str, float]) -> list[tuple[str, str, float]]:
    """Greedy settlement algorithm: who pays whom and how much."""
    eps = 0.01
    creditors = [[m, b] for m, b in balances.items() if b > eps]
    debtors = [[m, -b] for m, b in balances.items() if b < -eps]

    creditors.sort(key=lambda x: x[1], reverse=True)
    debtors.sort(key=lambda x: x[1], reverse=True)

    settlements = []
    i, j = 0, 0

    while i < len(debtors) and j < len(creditors):
        debtor, debt_amt = debtors[i]
        creditor, cred_amt = creditors[j]
        transfer = min(debt_amt, cred_amt)
        settlements.append((debtor, creditor, round(transfer, 2)))
        debtors[i][1] -= transfer
        creditors[j][1] -= transfer
        if debtors[i][1] < eps:
            i += 1
        if creditors[j][1] < eps:
            j += 1

    return settlements
