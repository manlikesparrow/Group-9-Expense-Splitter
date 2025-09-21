try:
    from src.core import Group, Expense, compute_settlements
except ImportError:
    from core import Group, Expense, compute_settlements

def demo():
    g = Group("Trip")
    g.add_member("Israel")
    g.add_member("Jomi")
    g.add_member("Meena")
    g.add_member("Clinton")

    g.add_expense(Expense(90, "Israel", ["Israel","Jomi","Meena", "Clinton"], "Hotel", category="Lodging"))
    g.add_expense(Expense(60, "Jomi", ["Israel","Jomi"], "Dinner", category="Food"))
    g.add_expense(Expense(30, "Meena", ["Jomi","Meena"], "Snacks", category="Food"))
    g.add_expense(Expense(15, "Clinton", ["Meena","Clinton" ], "Drinks", category="Food"))

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
