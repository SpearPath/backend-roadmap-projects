# Expense Tracker CLI

A lightweight, robust command-line interface to manage personal finances, track expenses, set monthly budgets, and view summaries with pluggable database persistence (**SQLite** default & **PostgreSQL** support).

Built as part of the [roadmap.sh Backend Developer Roadmap (Project 03: Expense Tracker)](https://roadmap.sh/projects/expense-tracker).

---

## Features

- **CRUD Operations**: Add, update, delete, and list expenses.
- **Financial Precision**: Uses Python's `Decimal` type to eliminate floating-point precision inaccuracies.
- **Categorization**: Group expenses by category (e.g. `Food`, `Transport`, `Bills`) and filter lists by category.
- **Monthly Summaries**: View total expenses overall or broken down by specific months.
- **Budget Tracking & Alerts**: Set a monthly budget threshold (`set-budget`) and receive automatic warnings if new expenses exceed the allocated budget.
- **CSV Data Export**: Export expense records to standard CSV files for external accounting.
- **Pluggable Database Architecture**:
  - **SQLite** (Default): Embedded, zero-configuration local database (`expenses.db`).
  - **PostgreSQL**: Production-grade client-server database configured via `DATABASE_URL` in `.env`.
- **Test-Driven Development (TDD)**: Comprehensive unit test suite with 37 tests covering domain models, persistence, service logic, and CLI commands.

---

## Project Structure

```text
03-expense-tracker-cli/
├── pyproject.toml              # Packaging metadata & console_scripts entry point
├── README.md                   # Project documentation & command guide
├── .gitignore                  # Git exclusions for DBs, env, and test artifacts
├── .env.example                # Sample database configuration
├── main.py                     # CLI entry point script
├── src/
│   ├── __init__.py
│   ├── models.py               # Expense & Budget dataclasses with Decimal validation
│   ├── expense_service.py      # Business logic, budget alerts, and CSV exporter
│   ├── cli.py                  # Argument parser & table formatters
│   └── repository/
│       ├── __init__.py
│       ├── base.py             # Abstract ExpenseRepository interface
│       ├── sqlite_repo.py      # SQLite implementation
│       └── postgres_repo.py    # PostgreSQL implementation (psycopg/psycopg2)
└── tests/
    ├── __init__.py
    ├── test_models.py          # Domain model & validation tests
    ├── test_repository.py      # Database CRUD and aggregation tests
    ├── test_service.py         # Business logic, budget alert & CSV export tests
    └── test_cli.py             # CLI argument parsing and output tests
```

---

## Usage Guide

You can now run `expense-tracker` directly in your terminal from anywhere without typing `python main.py`:

### 1. Adding an Expense
```bash
expense-tracker add --description "Lunch with team" --amount 25.50 --category Food
# Output: # Expense added successfully (ID: 1)
```

### 2. Listing Expenses
```bash
# List all expenses
expense-tracker list

# Filter by category
expense-tracker list --category Food
```

### 3. Viewing Expense Summaries
```bash
# Overall summary
expense-tracker summary
# Output: # Total expenses: $25.50

# Summary for a specific month (e.g. October)
expense-tracker summary --month 10
# Output: # Total expenses for October: $25.50
```

### 4. Updating an Expense
```bash
expense-tracker update --id 1 --description "Steak Dinner" --amount 45.00 --category Dining
# Output: # Expense updated successfully
```

### 5. Setting a Monthly Budget & Receiving Alerts
```bash
# Set a $50.00 budget for month 10 (October)
expense-tracker set-budget --month 10 --amount 50.00

# When an added expense pushes the monthly total above the budget:
expense-tracker add --description "Grocery run" --amount 30.00 --category Food
# Output:
# # Expense added successfully (ID: 2)
# [ALERT] Warning: You have exceeded your monthly budget of $50.00 for October 2026! Current total spent: $75.00
```

### 6. Exporting to CSV
```bash
expense-tracker export --file my_expenses.csv
# Output: # Expenses exported to my_expenses.csv
```

### 7. Deleting an Expense
```bash
expense-tracker delete --id 1
# Output: # Expense deleted successfully
```

---

## Database Configuration

### Using SQLite (Default)
No setup required. The application automatically initializes and maintains `expenses.db` in the project directory.

### Using PostgreSQL
1. Create a `.env` file from [.env.example](file:///.env.example):
   ```ini
   DATABASE_URL=postgresql://username:password@localhost:5432/expense_tracker
   ```
2. Install the PostgreSQL driver:
   ```bash
   pip install psycopg[binary]
   ```

---

## Running the Test Suite

Run the full unit test suite using Python's built-in `unittest` runner:
```bash
python -m unittest discover tests
```
