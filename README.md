# Group-9-Expense-Splitter-App

## Project Summary

The Expense Splitter App allows users to add group members, record shared expenses, and automatically compute simplified “who owes who” settlements. This helps groups split bills fairly without confusion.  
Built with **Python 3.13+, Tkinter, pandas, and matplotlib**.

---

## Features

### Core Logic
- `Expense`, `Group`, and settlement algorithm (`compute_settlements`)
- Validation for invalid participants and amounts

### CLI Demo
- Quick demonstration of balances and settlements

### Tkinter GUI Dashboard
- Manage group members
- Add expenses with:
  - Amount ($ placeholder)
  - Payer
  - Participants
  - Description
  - Category
- Transaction list with **category and month filters**
- Balances panel with **color coding** (green = receives, red = owes)
- Settlements panel with **color-coded pay/receive**
- Dashboard summary tiles:
  - **Total Balance** (updates dynamically)
  - **Monthly Spend** (updates dynamically)
- Charts (if activated):
  - Pie chart of **category distribution (current month)**
  - Bar chart of **monthly spend (last 6 months)**
- CSV Import:
  - Normalize column names automatically (`amount`, `payer`, `date`, `description`, `category`, `participants`)
  - Auto-add missing members during import
- CSV Export:
  - Export **balances**, **settlements**, or **transactions** to CSV
- Clear balances/settlements panel button
- Toggle view mode: **Summary** or **Selected Expense**

### Tests
- Core logic tested with pytest


## Getting Started

### Prerequisites
- Python 3.13+
- [Pipenv](https://pipenv.pypa.io/en/latest/)

### Setup
```bash
git clone https://github.com/manlikesparrow/Group-9-Expense-Splitter.git
cd Group-9-Expense-Splitter

pipenv --python 3.13
pipenv install
pipenv install --dev pytest
```

### Usage
Run CLI Demo:
```bash:
pipenv run python src/main.py
```
Run GUI Dashboard:
```bash:
pipenv run python -m src.gui
# OR
pipenv run python src/gui.py
```

### CSV Format

When importing, your CSV should contain at least:

Amount

Payer

Optional columns:

Date (any parseable format)

Description

Category

Participants (comma-separated list)

### Example CSV:

Date,Amount,Payer,Participants,Category,Description
2025-09-01,90,Alice,"Alice,Bob,Carol",Lodging,Hotel
2025-09-02,60,Bob,"Alice,Bob",Food,Dinner
2025-09-03,30,Carol,"Bob,Carol",Food,Snacks

### Testing

Run all tests:
```bash
pipenv run pytest -q
# OR
pytest
```

### Roles

Clinton Ndubueze – Leader / Coordinator

Israel Longji Luka – Developer (Core Logic & GUI Fixes)

Sulaiman Rabiu – Developer (Demo)

Taheer Ibrahim Maibiu – Documentation

Olakanmi Oluwatobiloba – Q/A (CI)

Amina Gujbawu – Developer (GUI)

Agudiegwu Kamsiyochi Unique – Developer (Data)

Ajani Oluwajomiloju – Developer (UI)

Timothy Celina – Presenter

Nduwuba Daniel Chemuachefulam – Q/A (Test)

### Link to Demo Video

https://drive.google.com/file/d/1K8iSnaGbCyEZe-0wglafgPlndCkHRzTN/view?usp=sharing

### Screenshots

MacOS: docs/mac_screenshot

Windows: docs/windows_screenshot
