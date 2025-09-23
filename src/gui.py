# src/gui.py
# Run: python -m src.gui  or python src/gui.py
import tkinter as tk
from tkinter import ttk, messagebox, filedialog
import csv
from datetime import datetime
# Import core with fallback
try:
    from src.core import Group, Expense, compute_settlements
except ImportError:
    from core import Group, Expense, compute_settlements


class ExpenseApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Group 9: Expense Splitter Dashboard")
        self.group = Group("Dashboard Group")
        self.tree_item_map = {}

        # ------ Summary Tiles ------
        frame_summary = ttk.Frame(root)
        frame_summary.pack(fill="x", padx=8, pady=6)

        self.total_balance_label = ttk.Label(frame_summary, text="Total Balance: $0.00", font=("Arial", 12, "bold"))
        self.total_balance_label.pack(side="left", padx=12)

        self.monthly_spend_label = ttk.Label(frame_summary, text="Monthly Spend: $0.00", font=("Arial", 12, "bold"))
        self.monthly_spend_label.pack(side="left", padx=12)

        # ------ Member Management ------
        frame_members = ttk.LabelFrame(root, text="Group Members")
        frame_members.pack(fill="x", padx=8, pady=6)

        self.member_entry = ttk.Entry(frame_members, width=25)
        self.member_entry.pack(side="left", padx=6, pady=6)
        ttk.Button(frame_members, text="Add Member", command=self.add_member).pack(side="left", padx=6)
        self.members_label = ttk.Label(frame_members, text="Members: []")
        self.members_label.pack(side="left", padx=12)

        # ------ Expense Form ------
        frame_expense = ttk.LabelFrame(root, text="Add Expense")
        frame_expense.pack(fill="x", padx=8, pady=6)

        ttk.Label(frame_expense, text="Amount ($):").grid(row=0, column=0, sticky="w", padx=4, pady=2)
        self.amount_entry = ttk.Entry(frame_expense, width=18)
        self.amount_entry.grid(row=0, column=1, padx=4, pady=2)
        self.amount_entry.insert(0, "$")
        self.amount_entry.bind("<FocusIn>", self._clear_amount_placeholder)
        self.amount_entry.bind("<FocusOut>", self._restore_amount_placeholder)

        ttk.Label(frame_expense, text="Payer:").grid(row=1, column=0, sticky="w", padx=4, pady=2)
        self.payer_entry = ttk.Entry(frame_expense, width=18)
        self.payer_entry.grid(row=1, column=1, padx=4, pady=2)

        ttk.Label(frame_expense, text="Participants (comma separated):").grid(row=2, column=0, sticky="w", padx=4, pady=2)
        self.participants_entry = ttk.Entry(frame_expense, width=40)
        self.participants_entry.grid(row=2, column=1, padx=4, pady=2, columnspan=2)

        ttk.Label(frame_expense, text="Description:").grid(row=3, column=0, sticky="w", padx=4, pady=2)
        self.desc_entry = ttk.Entry(frame_expense, width=40)
        self.desc_entry.grid(row=3, column=1, padx=4, pady=2, columnspan=2)

        ttk.Label(frame_expense, text="Category:").grid(row=4, column=0, sticky="w", padx=4, pady=2)
        self.category_entry = ttk.Entry(frame_expense, width=25)
        self.category_entry.grid(row=4, column=1, padx=4, pady=2)

        ttk.Button(frame_expense, text="Add Expense", command=self.add_expense).grid(row=5, column=0, columnspan=3, pady=6)

        # ------ Transaction List & Filters ------
        frame_list = ttk.LabelFrame(root, text="Transactions")
        frame_list.pack(fill="both", expand=False, padx=8, pady=6)

        controls = ttk.Frame(frame_list)
        controls.pack(fill="x", padx=6, pady=4)

        ttk.Button(controls, text="Import CSV", command=self.import_csv).pack(side="left", padx=4)
        ttk.Button(controls, text="Export Balances (CSV)", command=self.export_balances).pack(side="left", padx=4)
        ttk.Button(controls, text="Export Settlements (CSV)", command=self.export_settlements).pack(side="left", padx=4)
        ttk.Button(controls, text="Export Transactions (CSV)", command=self.export_transactions).pack(side="left", padx=4)

        # Filters
        ttk.Label(controls, text="Category:").pack(side="left", padx=2)
        self.category_var = tk.StringVar(value="All")
        self.category_dropdown = ttk.Combobox(controls, textvariable=self.category_var, state="readonly")
        self.category_dropdown.pack(side="left", padx=2)
        self.category_dropdown.bind("<<ComboboxSelected>>", lambda e: self.refresh_dashboard())

        ttk.Label(controls, text="Month:").pack(side="left", padx=2)
        self.month_var = tk.StringVar(value="All")
        self.month_dropdown = ttk.Combobox(controls, textvariable=self.month_var, state="readonly",
                                           values=["All"] + [str(m) for m in range(1, 13)])
        self.month_dropdown.pack(side="left", padx=2)
        self.month_dropdown.bind("<<ComboboxSelected>>", lambda e: self.refresh_dashboard())

        self.tree = ttk.Treeview(frame_list, columns=("Date", "Payer", "Amount", "Category", "Description"), show="headings", height=8)
        for col in self.tree["columns"]:
            self.tree.heading(col, text=col)
            self.tree.column(col, width=120)
        self.tree.pack(fill="both", expand=True, padx=6, pady=6)
        self.tree.bind("<<TreeviewSelect>>", self.on_tree_select)

        try:
            self.tree.tag_configure('highlight', background='#fff59d')
        except Exception:
            pass

        # ------ Balances & Settlements ------
        frame_panels = ttk.Frame(root)
        frame_panels.pack(fill="both", expand=False, padx=8, pady=6)

        left_panel = ttk.LabelFrame(frame_panels, text="Balances")
        left_panel.pack(side="left", fill="both", expand=True, padx=4)

        self.balance_title = ttk.Label(left_panel, text="(No expenses yet)", font=("Arial", 10, "bold"))
        self.balance_title.pack()
        self.balances_text = tk.Text(left_panel, height=8, width=40)
        self.balances_text.pack(padx=4, pady=6)
        self.balances_text.tag_config("receives", foreground="green")
        self.balances_text.tag_config("owes", foreground="red")
        self.balances_text.tag_config("settled", foreground="black")

        right_panel = ttk.LabelFrame(frame_panels, text="Settlements")
        right_panel.pack(side="left", fill="both", expand=True, padx=4)

        self.settlement_title = ttk.Label(right_panel, text="(No expenses yet)", font=("Arial", 10, "bold"))
        self.settlement_title.pack()
        self.settlements_text = tk.Text(right_panel, height=8, width=40)
        self.settlements_text.pack(padx=4, pady=6)

        # Clear button
        ttk.Button(root, text="Clear Balances/Settlements", command=self.clear_display).pack(pady=4)

        # ------ View Mode Toggle ------
        frame_mode = ttk.Frame(root)
        frame_mode.pack(fill="x", padx=8, pady=4)
        self.view_mode = tk.StringVar(value="summary")
        ttk.Label(frame_mode, text="View mode:").pack(side="left", padx=(0,6))
        ttk.Radiobutton(frame_mode, text="Summary", variable=self.view_mode, value="summary", command=self.refresh_dashboard).pack(side="left", padx=6)
        ttk.Radiobutton(frame_mode, text="Selected Expense", variable=self.view_mode, value="selected", command=self.refresh_dashboard).pack(side="left", padx=6)

        # Initial refresh
        self.refresh_dashboard()

    # ---------- Helpers ----------
    def _clear_amount_placeholder(self, event):
        if self.amount_entry.get().strip() == "$":
            self.amount_entry.delete(0, tk.END)

    def _restore_amount_placeholder(self, event):
        if not self.amount_entry.get().strip():
            self.amount_entry.insert(0, "$")

    def clear_display(self):
        self.balances_text.delete("1.0", tk.END)
        self.settlements_text.delete("1.0", tk.END)
        self.balance_title.config(text="(Cleared)")
        self.settlement_title.config(text="(Cleared)")

    def _refresh_treeview(self, expenses):
        """Refresh the TreeView to display only the given expenses."""
        for item in self.tree.get_children():
            self.tree.delete(item)
        self.tree_item_map.clear()

        for exp in expenses:
            item = self.tree.insert(
                "", "end",
                values=(exp.date.isoformat(), exp.payer, f"${exp.amount:.2f}", exp.category, exp.description)
            )
            self.tree_item_map[item] = exp

    # ---------- Member / Expense ----------
    def add_member(self):
        member = self.member_entry.get().strip()
        if not member:
            messagebox.showerror("Error", "Member name cannot be empty")
            return
        try:
            self.group.add_member(member)
            self.member_entry.delete(0, tk.END)
            self.members_label.config(text=f"Members: {', '.join(self.group.members)}")
            self.refresh_dashboard()
        except Exception as e:
            messagebox.showerror("Error", str(e))

    def add_expense(self):
        try:
            text = self.amount_entry.get().strip().lstrip('$').replace(',', '')
            amount = float(text)
            payer = self.payer_entry.get().strip()
            participants = [p.strip() for p in self.participants_entry.get().split(",") if p.strip()]
            desc = self.desc_entry.get().strip()
            category = self.category_entry.get().strip() or "Uncategorized"

            # Validate members exist
            missing = {p for p in participants + [payer] if p not in self.group.members}
            if missing:
                messagebox.showerror("Error", f"Missing members: {', '.join(missing)}. Add them first.")
                return

            exp = Expense(amount, payer, participants, desc, category, date=datetime.now().date())
            self.group.add_expense(exp)

            self.member_entry.delete(0, tk.END)
            self.amount_entry.delete(0, tk.END)
            self.participants_entry.delete(0, tk.END)
            self.desc_entry.delete(0, tk.END)
            self.category_entry.delete(0, tk.END)
            self.payer_entry.delete(0, tk.END)

            self.refresh_dashboard()
        except ValueError:
            messagebox.showerror("Error", "Invalid amount")
        except Exception as e:
            messagebox.showerror("Error", str(e))

    # ---------- TreeView ----------
    def on_tree_select(self, event):
        if self.view_mode.get() == "selected":
            selected = self.tree.selection()
            if selected:
                item = selected[0]
                exp = self.tree_item_map.get(item)
                if exp:
                    balances, settlements = compute_settlements([exp])
                    self._display_balances(balances, settlements, title=f"Balances for: {exp.description}")
                else:
                    self.clear_display()
        else:
            self.refresh_dashboard()

    # ---------- Dashboard ----------
    def refresh_dashboard(self):
        # --- Filter expenses by category/month ---
        selected_category = self.category_var.get()
        selected_month = self.month_var.get()
        filtered_expenses = self.group.expenses
        if selected_category != "All":
            filtered_expenses = [e for e in filtered_expenses if e.category == selected_category]
        if selected_month != "All":
            filtered_expenses = [e for e in filtered_expenses if e.date.month == int(selected_month)]

        # --- Update Category Dropdown dynamically ---
        categories = ["All"] + sorted({e.category for e in self.group.expenses})
        self.category_dropdown["values"] = categories
        if selected_category not in categories:
            self.category_var.set("All")

        # --- Refresh TreeView ---
        self._refresh_treeview(filtered_expenses)

        # --- Compute totals for summary tiles ---
        total_balance = sum([e.amount for e in filtered_expenses])
        self.total_balance_label.config(text=f"Total Balance: ${total_balance:.2f}")

        current_month = datetime.now().month
        monthly_spend = sum([e.amount for e in filtered_expenses if e.date.month == current_month])
        self.monthly_spend_label.config(text=f"Monthly Spend: ${monthly_spend:.2f}")

        # --- Display balances and settlements ---
        if self.view_mode.get() == "summary":
            balances, settlements = compute_settlements(filtered_expenses)
            self._display_balances(balances, settlements, title="Balances & Settlements")

    def _display_balances(self, balances, settlements, title="Balances & Settlements"):
        self.balances_text.delete("1.0", tk.END)
        self.settlements_text.delete("1.0", tk.END)
        self.balance_title.config(text=title)
        self.settlement_title.config(text=title)

        for member, amt in balances.items():
            tag = "receives" if amt > 0 else "owes" if amt < 0 else "settled"
            self.balances_text.insert(tk.END, f"{member}: ${amt:.2f}\n", tag)

        for s in settlements:
            self.settlements_text.insert(tk.END, f"{s[0]} pays {s[1]}: ${s[2]:.2f}\n")

    # ---------- CSV Import/Export ----------
    def import_csv(self):
        path = filedialog.askopenfilename(filetypes=[("CSV files","*.csv")])
        if not path:
            return
        try:
            with open(path, newline='') as f:
                reader = csv.DictReader(f)
                for row in reader:
                    payer = row['payer']
                    participants = row['participants'].split(",")
                    for m in [payer] + participants:
                        if m not in self.group.members:
                            self.group.add_member(m)
                    exp = Expense(
                        float(row['amount']),
                        payer,
                        participants,
                        row.get('description', ''),
                        row.get('category', 'Uncategorized'),
                        date=datetime.strptime(row['date'], "%Y-%m-%d").date()
                    )
                    self.group.add_expense(exp)
            self.members_label.config(text=f"Members: {', '.join(self.group.members)}")
            self.refresh_dashboard()
        except Exception as e:
            messagebox.showerror("Error", str(e))

    def export_balances(self):
        balances, _ = compute_settlements(self.group.expenses)
        path = filedialog.asksaveasfilename(defaultextension=".csv")
        if not path:
            return
        try:
            with open(path, "w", newline="") as f:
                writer = csv.writer(f)
                writer.writerow(["Member","Balance"])
                for m, amt in balances.items():
                    writer.writerow([m, amt])
        except Exception as e:
            messagebox.showerror("Error", str(e))

    def export_settlements(self):
        _, settlements = compute_settlements(self.group.expenses)
        path = filedialog.asksaveasfilename(defaultextension=".csv")
        if not path:
            return
        try:
            with open(path, "w", newline="") as f:
                writer = csv.writer(f)
                writer.writerow(["From","To","Amount"])
                for s in settlements:
                    writer.writerow(s)
        except Exception as e:
            messagebox.showerror("Error", str(e))

    def export_transactions(self):
        path = filedialog.asksaveasfilename(defaultextension=".csv")
        if not path:
            return
        try:
            with open(path, "w", newline="") as f:
                writer = csv.writer(f)
                writer.writerow(["date","payer","amount","category","description","participants"])
                for exp in self.group.expenses:
                    writer.writerow([exp.date.isoformat(), exp.payer, exp.amount, exp.category, exp.description, ",".join(exp.participants)])
        except Exception as e:
            messagebox.showerror("Error", str(e))


if __name__ == "__main__":
    root = tk.Tk()
    app = ExpenseApp(root)
    root.mainloop()
