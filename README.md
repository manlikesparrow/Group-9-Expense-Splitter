# Group 9: Expense Splitter App

📌 Project Summary
The Expense Splitter App allows users to add group members, record shared expenses, and automatically compute simplified “who owes who” settlements. This helps groups split bills fairly without confusion.

🎯 MVP Acceptance Criteria
- A user can add a group and expenses.
- The app will show the net balance per person
- The app will generate a minimal settlement suggestion


🛠️ Tech Stack & Requirements
- Python: 3.10+
- Dependency Management: pipenv (`Pipfile` + `Pipfile.lock`)
- Testing: pytest (at least 2 passing tests)
- Version Control: GitHub repository with meaningful commits
- Optional: GitHub Actions CI to run pytest on every push


🚀 Setup & Run Instructions
Clone the repository and install dependencies:

In Terminal: 
-git clone https://github.com/manlikesparrow/Group-9-Expense-Splitter.git
-cd Group-9-Expense-Splitter
-pip install
-pipenv install

Run the app:
python src/main.py

Run tests:
pytest -q
