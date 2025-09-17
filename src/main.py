# run as: python src/main.py
try:
    from src.core import Group, Expense, compute_settlements
except ImportError:
    from core import Group, Expense, compute_settlements

def demo():
    g = Group("Trip")
    g.add_member("Alice")
    g.add_member("Bob")
    g.add_member("Carol")

    g.add_expense(Expense(90, "Alice", ["Alice","Bob","Carol"], "Hotel", category="Lodging"))
    g.add_expense(Expense(60, "Bob", ["Alice","Bob"], "Dinner", category="Food"))
    g.add_expense(Expense(30, "Carol", ["Bob","Carol"], "Snacks", category="Food"))

    print("=== Balances ===")
    balances = g.net_balances()
    for m, b in balances.items():
        status = "receives" if b>0 else "owes" if b<0 else "settled"
        print(f"{m}: ${b:.2f} ({status})")

    print("\n=== Settlements ===")
    for fr, to, amt in compute_settlements(balances):
        print(f"{fr} pays {to}: ${amt:.2f}")

if __name__ == "__main__":
    demo()
