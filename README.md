# Group-9-Expense-Splitter-App

# Project Summary

The Expense Splitter App allows users to add group members, record shared expenses, and automatically compute simplified “who owes who” settlements. This helps groups split bills fairly without confusion.
Built with **Python 3.13+, Tkinter, pandas, and matplotlib**.




## Features
- **Core Logic**
  - `Expense`, `Group`, and settlement algorithm (`compute_settlements`)
  - Validation for invalid participants and amounts
- **CLI Demo**
  - Quick demonstration of balances and settlements
- **Tkinter GUI Dashboard**
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
    - **Total Balance**
    - **Monthly Spend**
  - Charts (IF active):
    - Pie chart of **category distribution (current month)**
    - Bar chart of **monthly spend (last 6 months)**
  - CSV Import:
    - Normalize column names automatically (amount, payer, date, description, category, participants)
    - Auto-add missing members during import
  - CSV Export:
    - Export **balances** or **transactions** to CSV
- **Tests**
  - Core logic tested with pytest

## Getting Started

### Prerequisites
- Python 3.10
- [Pipenv](https://pipenv.pypa.io/en/latest/)

### Setup
Terminal/bash/cmd:

git clone https://github.com/manlikesparrow/Group-9-Expense-Splitter.git
cd group09-expense-splitter

pipenv --python 3.13
pipenv install
pipenv install --dev pytest

### Usage
In Terminal:
Run CLI Demo
pipenv run python src/main.py

In Terminal:
Run GUI Dashboard
pipenv run python -m src.gui

### CSV Format

When importing, your CSV should contain at least:

Amount

Payer

Optional columns:

Date (any parseable format)

Description

Category

Participants (comma-separated list)

Example:
Date,Amount,Payer,Participants,Category,Description
2025-09-01,90,Alice,"Alice,Bob,Carol",Lodging,Hotel
2025-09-02,60,Bob,"Alice,Bob",Food,Dinner
2025-09-03,30,Carol,"Bob,Carol",Food,Snacks

### Testing

Run all tests:

pipenv run pytest -q
OR 
pytest

### Roles
1.	Clinton Ndubueze – Leader / Coordinator
2.	Israel Longji Luka – Developer (Core Logic)
3.	Sulaiman Rabiu – Developer (Demo)
4.	Taheer Ibrahim Maibiu – Documentation
5.	Olakanmi Oluwatobiloba – Q/A (CI)
6.	Amina Gujbawu – Developer (GUI)
7.	Agudiegwu Kamsiyochi Unique – Developer (Data)
8.	Ajani Oluwajomiloju – Developer (UI)
9.	Timothy Celina – Presenter
10.	Nduwuba Daniel Chemuachefulam – Q/A (Test)

### Link to  first Demo video
https://drive.google.com/file/d/1K8iSnaGbCyEZe-0wglafgPlndCkHRzTN/view?usp=sharing

##Link to Full Demo video
https://drive.google.com/file/d/1HnsesHV5MqmMOH6Yewc2-YYk_Zs_bQm8/view?usp=drive_link

## Screenshots
MacOS screenshots of fully working app: docs/mac_screenshot 
Windows screenshots of fully working app: docs/windows_screenshot 