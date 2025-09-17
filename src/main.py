# src/main.py
from core import Group, Expense, compute_settlements

def demo():
    print("=" * 40)
    print("   Group 9:💵 Expense Splitter Demo")
    print("=" * 40)

    # Create group
    g = Group("Trip to Lagos 🛫")
    g.add_member("Israel")
    g.add_member("Jomi")
    g.add_member("Meena")

    print(f"\nGroup Title: {g.name}")
    print("Members/Participants:", ", ".join(g.members))

    # Add some expenses
    g.add_expense(Expense(93.45, "Israel", ["Israel", "Jomi", "Meena"], "Hotel"))
    g.add_expense(Expense(64.23, "Jomi", ["Israel", "Jomi"], "Dinner"))
    g.add_expense(Expense(30.19, "Meena", ["Jomi", "Meena"], "Snacks"))

    print("\nExpenses recorded:")
    for e in g.expenses:
        print(f" - {e.description}: {e.amount} paid by {e.payer} for: {', '.join(e.participants)}")

    # Show balances
    print("\n=== Balances ===")
    balances = g.net_balances()
    for member, bal in balances.items():
        status = "should receive" if bal > 0 else "owes" if bal < 0 else "settled"
        print(f"{member:>5}: {bal:>6.2f} ({status})")

    # Show settlement suggestions
    print("\n=== Settlement Suggestions ===")
    settlements = compute_settlements(balances)
    if not settlements:
        print("All balances are settled!")
    else:
        for fr, to, amt in settlements:
            print(f"{fr} pays {to}: {amt:.2f}")

    print("\nDemo completed ✅")

if __name__ == "__main__":
    demo()
