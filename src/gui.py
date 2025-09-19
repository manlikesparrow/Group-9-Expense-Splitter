# run as: python -m src.gui  OR  python src/gui.py
import tkinter as tk
from tkinter import ttk, messagebox, filedialog
import csv
from datetime import datetime
import pandas as pd

# Import core with fallback so running as script or package both work
try:
    from src.core import Group, Expense, compute_settlements
except ImportError:
    from core import Group, Expense, compute_settlements


class ExpenseApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Group 9: Expense Splitter Dashboard")
        self.group = Group("Dashboard Group")
        self.tree_item_map = {}  # map tree item id -> Expense object

        # ------ Top summary tiles ------
        frame_summary = ttk.Frame(root)
        frame_summary.pack(fill="x", padx=8, pady=6)

        self.total_balance_label = ttk.Label(frame_summary, text="Total Balance: $0.00", font=("Arial", 12, "bold"))
        self.total_balance_label.pack(side="left", padx=12)

        self.monthly_spend_label = ttk.Label(frame_summary, text="Monthly Spend: $0.00", font=("Arial", 12, "bold"))
        self.monthly_spend_label.pack(side="left", padx=12)

        # ------ Members management ------
        frame_members = ttk.LabelFrame(root, text="Group Members")
        frame_members.pack(fill="x", padx=8, pady=6)

        self.member_entry = ttk.Entry(frame_members, width=25)
        self.member_entry.pack(side="left", padx=6, pady=6)
        ttk.Button(frame_members, text="Add Member", command=self.add_member).pack(side="left", padx=6)
        self.members_label = ttk.Label(frame_members, text="Members: []")
        self.members_label.pack(side="left", padx=12)

        # ------ Expense form ------
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

        # ------ Transaction list + controls ------
        frame_list = ttk.LabelFrame(root, text="Transactions")
        frame_list.pack(fill="both", expand=False, padx=8, pady=6)

        controls = ttk.Frame(frame_list)
        controls.pack(fill="x", padx=6, pady=4)

        ttk.Button(controls, text="Import CSV", command=self.import_csv).pack(side="left", padx=4)
        ttk.Button(controls, text="Export Balances (CSV)", command=self.export_balances).pack(side="left", padx=4)
        ttk.Button(controls, text="Export Transactions (CSV)", command=self.export_transactions).pack(side="left", padx=4)

        ttk.Label(controls, text="Category filter:").pack(side="left", padx=(12,4))
        self.category_filter = ttk.Combobox(controls, values=["All"], state="readonly", width=20)
        self.category_filter.current(0)
        self.category_filter.pack(side="left", padx=4)
        self.category_filter.bind("<<ComboboxSelected>>", lambda e: self.refresh_dashboard())

        ttk.Label(controls, text="Month filter:").pack(side="left", padx=(12,4))
        self.month_filter = ttk.Combobox(controls, values=["All"], state="readonly", width=12)
        self.month_filter.current(0)
        self.month_filter.pack(side="left", padx=4)
        self.month_filter.bind("<<ComboboxSelected>>", lambda e: self.refresh_dashboard())

        cols = ("Date", "Payer", "Amount", "Category", "Description")
        self.tree = ttk.Treeview(frame_list, columns=cols, show="headings", height=8)
        for c in cols:
            self.tree.heading(c, text=c)
            self.tree.column(c, width=110, anchor="center")
        self.tree.pack(fill="both", expand=True, padx=6, pady=6)
        self.tree.bind("<<TreeviewSelect>>", self.on_tree_select)

        frame_edit = ttk.Frame(frame_list)
        frame_edit.pack(fill="x", padx=6, pady=(0,6))
        ttk.Label(frame_edit, text="Selected category:").pack(side="left", padx=4)
        self.selected_category_entry = ttk.Entry(frame_edit, width=20)
        self.selected_category_entry.pack(side="left", padx=4)
        ttk.Button(frame_edit, text="Update Category", command=self.update_selected_category).pack(side="left", padx=6)

        # ------ Balances & settlements panels ------
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
        self.settlements_text.tag_config("payer", foreground="red")
        self.settlements_text.tag_config("receiver", foreground="green")
        self.settlements_text.tag_config("amount", font=("Arial", 10, "bold"))

        # Initial refresh
        self.refresh_dashboard()

    # ---------- helper for amount placeholder ----------
    def _clear_amount_placeholder(self, event):
        if self.amount_entry.get().strip() == "$":
            self.amount_entry.delete(0, tk.END)

    def _restore_amount_placeholder(self, event):
        if not self.amount_entry.get().strip():
            self.amount_entry.insert(0, "$")

    # ---------- members ----------
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

    # ---------- expenses ----------
    def add_expense(self):
        try:
            text = self.amount_entry.get().strip()
            text = text.lstrip('$').replace(',', '')
            amount = float(text)
            payer = self.payer_entry.get().strip()
            participants = [p.strip() for p in self.participants_entry.get().split(",") if p.strip()]
            desc = self.desc_entry.get().strip()
            category = self.category_entry.get().strip() or "Uncategorized"
            exp = Expense(amount, payer, participants, desc, category, date=datetime.now().date())
            self.group.add_expense(exp)
            item = self.tree.insert("", "end", values=(exp.date.isoformat(), exp.payer, f"${exp.amount:.2f}", exp.category, exp.description))
            self.tree_item_map[item] = exp
            self.amount_entry.delete(0, tk.END); self.amount_entry.insert(0, "$")
            self.payer_entry.delete(0, tk.END)
            self.participants_entry.delete(0, tk.END)
            self.desc_entry.delete(0, tk.END)
            self.category_entry.delete(0, tk.END)
            self.refresh_dashboard()
        except Exception as e:
            messagebox.showerror("Error", str(e))

    # ---------- tree selection ----------
    def on_tree_select(self, event):
        sel = self.tree.selection()
        if not sel:
            return
        item = sel[0]
        exp = self.tree_item_map.get(item)
        if exp:
            self.selected_category_entry.delete(0, tk.END)
            self.selected_category_entry.insert(0, exp.category)

    def update_selected_category(self):
        sel = self.tree.selection()
        if not sel:
            messagebox.showinfo("Info", "Select a transaction to update.")
            return
        new_cat = self.selected_category_entry.get().strip() or "Uncategorized"
        item = sel[0]
        exp = self.tree_item_map.get(item)
        if exp:
            exp.category = new_cat
            self.tree.item(item, values=(exp.date.isoformat(), exp.payer, f"${exp.amount:.2f}", exp.category, exp.description))
            self.refresh_dashboard()

    # ---------- filters & tree ----------
    def update_filters(self):
        cats = set(e.category for e in self.group.expenses)
        cat_list = ["All"] + sorted(cats)
        self.category_filter['values'] = cat_list
        if self.category_filter.get() not in cat_list:
            self.category_filter.set("All")

        months = sorted({e.date.strftime("%Y-%m") for e in self.group.expenses}, reverse=True)
        month_list = ["All"] + months
        self.month_filter['values'] = month_list
        if self.month_filter.get() not in month_list:
            self.month_filter.set("All")

    def refresh_dashboard(self):
        self.update_filters()
        self.tree.delete(*self.tree.get_children())
        self.tree_item_map.clear()
        cat_filter = self.category_filter.get()
        month_filter = self.month_filter.get()
        for exp in self.group.expenses:
            if cat_filter and cat_filter != "All" and exp.category != cat_filter:
                continue
            if month_filter and month_filter != "All" and exp.date.strftime("%Y-%m") != month_filter:
                continue
            item = self.tree.insert("", "end", values=(exp.date.isoformat(), exp.payer, f"${exp.amount:.2f}", exp.category, exp.description))
            self.tree_item_map[item] = exp

        balances = self.group.net_balances()
        total_balance = sum(balances.values())
        now = datetime.now()
        monthly_spend = sum(e.amount for e in self.group.expenses if (e.date.year == now.year and e.date.month == now.month))
        self.total_balance_label.config(text=f"Total Balance: ${total_balance:.2f}")
        self.monthly_spend_label.config(text=f"Monthly Spend: ${monthly_spend:.2f}")

        self.balance_title.config(text=f"Balances (last update: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')})")
        self.balances_text.delete("1.0", tk.END)
        for m, b in balances.items():
            tag = "receives" if b > 0 else "owes" if b < 0 else "settled"
            self.balances_text.insert(tk.END, f"{m}: ${b:.2f} ({'receives' if b>0 else 'owes' if b<0 else 'settled'})\n", tag)

        self.settlement_title.config(text=f"Settlements (last update: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')})")
        self.settlements_text.delete("1.0", tk.END)
        settlements = compute_settlements(balances)
        if not settlements:
            self.settlements_text.insert(tk.END, "All settled!\n")
        else:
            for fr, to, amt in settlements:
                self.settlements_text.insert(tk.END, fr, "payer")
                self.settlements_text.insert(tk.END, " pays ")
                self.settlements_text.insert(tk.END, to, "receiver")
                self.settlements_text.insert(tk.END, f": ${amt:.2f}\n", "amount")

    # ---------- CSV import ----------
    def import_csv(self):
        file = filedialog.askopenfilename(filetypes=[("CSV Files", "*.csv")])
        if not file:
            return
        try:
            df = pd.read_csv(file)
        except Exception as e:
            messagebox.showerror("Error", f"Could not read CSV: {e}")
            return

        cols = {c.lower().strip(): c for c in df.columns}
        def get_col(*keys, default=None):
            for k in keys:
                if k in cols:
                    return cols[k]
            return default

        col_date = get_col("date", "datetime", "timestamp")
        col_amount = get_col("amount", "amt", "value", "cost")
        col_payer = get_col("payer", "paid_by", "payee", "from")
        col_desc = get_col("description", "desc", "details")
        col_cat = get_col("category", "cat")

        if not col_amount or not col_payer:
            messagebox.showerror("Error", "CSV must contain at least 'Amount' and 'Payer' columns.")
            return

        added_members = set()
        skipped = 0
        for _, row in df.iterrows():
            try:
                amount = float(row[col_amount])
            except Exception:
                skipped += 1
                continue
            payer = str(row[col_payer]).strip()
            participants = []
            pcol = get_col("participants", "participant", "people")
            if pcol and pd.notna(row[pcol]):
                participants = [p.strip() for p in str(row[pcol]).split(",") if p.strip()]
            else:
                participants = [payer]

            desc = str(row[col_desc]) if col_desc and pd.notna(row[col_desc]) else ""
            category = str(row[col_cat]) if col_cat and pd.notna(row[col_cat]) else "Imported"
            if col_date and pd.notna(row[col_date]):
                try:
                    d = pd.to_datetime(row[col_date]).date()
                except Exception:
                    d = datetime.now().date()
            else:
                d = datetime.now().date()

            for m in [payer] + participants:
                if m and m not in self.group.members:
                    self.group.add_member(m)
                    added_members.add(m)

            try:
                exp = Expense(amount, payer, participants, desc, category, date=d)
                self.group.add_expense(exp)
                item = self.tree.insert("", "end", values=(exp.date.isoformat(), exp.payer, f"${exp.amount:.2f}", exp.category, exp.description))
                self.tree_item_map[item] = exp
            except Exception:
                skipped += 1
                continue

        self.members_label.config(text=f"Members: {', '.join(self.group.members)}")
        msg = f"Imported CSV. New members added: {', '.join(sorted(added_members))}" if added_members else "Imported CSV."
        if skipped:
            msg += f" ({skipped} rows skipped due to errors)"
        messagebox.showinfo("Import result", msg)
        self.refresh_dashboard()

    # ---------- Exports ----------
    def export_balances(self):
        balances = self.group.net_balances()
        path = filedialog.asksaveasfilename(defaultextension=".csv", filetypes=[("CSV Files","*.csv")])
        if not path:
            return
        with open(path, "w", newline="") as f:
            w = csv.writer(f)
            w.writerow(["Member", "Balance ($)"])
            for m, b in balances.items():
                w.writerow([m, f"{b:.2f}"])
        messagebox.showinfo("Export", f"Balances exported to {path}")

    def export_transactions(self):
        path = filedialog.asksaveasfilename(defaultextension=".csv", filetypes=[("CSV Files","*.csv")])
        if not path:
            return
        with open(path, "w", newline="") as f:
            w = csv.writer(f)
            w.writerow(["Date", "Payer", "Participants", "Amount", "Category", "Description"])
            for e in self.group.expenses:
                parts = ",".join(e.participants)
                w.writerow([e.date.isoformat(), e.payer, parts, f"{e.amount:.2f}", e.category, e.description])
        messagebox.showinfo("Export", f"Transactions exported to {path}")


def start():
    root = tk.Tk()
    app = ExpenseApp(root)
    root.mainloop()
