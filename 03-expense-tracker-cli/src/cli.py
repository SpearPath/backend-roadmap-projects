import argparse
import calendar
import os
import sys
from datetime import date
from decimal import Decimal
from typing import Optional, List

from src.models import Expense, Budget
from src.expense_service import ExpenseService
from src.repository.sqlite_repo import SQLiteExpenseRepository


def get_default_service() -> ExpenseService:
    """Factory to instantiate repository based on environment."""
    db_url = os.getenv("DATABASE_URL")
    if db_url and db_url.startswith("postgres"):
        try:
            from src.repository.postgres_repo import PostgreSQLExpenseRepository
            repo = PostgreSQLExpenseRepository(db_url)
            return ExpenseService(repo)
        except Exception as e:
            print(f"[Warning] Failed to connect to PostgreSQL ({e}). Falling back to SQLite.")

    # Default to SQLite local database
    db_file = os.getenv("EXPENSE_DB_PATH", "expenses.db")
    repo = SQLiteExpenseRepository(db_file)
    return ExpenseService(repo)


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="expense-tracker",
        description="A lightweight expense tracker CLI to manage personal finances.",
    )
    subparsers = parser.add_subparsers(dest="command", help="Available subcommands")

    # add
    add_parser = subparsers.add_parser("add", help="Add a new expense")
    add_parser.add_argument("--description", required=True, help="Description of the expense")
    add_parser.add_argument("--amount", required=True, type=str, help="Expense amount (e.g. 20.00)")
    add_parser.add_argument("--category", default="General", help="Category (default: General)")
    add_parser.add_argument("--date", default=None, help="Expense date YYYY-MM-DD (default: today)")

    # list
    list_parser = subparsers.add_parser("list", help="List all expenses")
    list_parser.add_argument("--category", default=None, help="Filter expenses by category")

    # summary
    summary_parser = subparsers.add_parser("summary", help="View total expense summary")
    summary_parser.add_argument("--month", type=int, default=None, help="Specific month (1-12)")
    summary_parser.add_argument("--year", type=int, default=None, help="Specific year (e.g. 2026)")

    # delete
    del_parser = subparsers.add_parser("delete", help="Delete an expense by ID")
    del_parser.add_argument("--id", required=True, type=int, help="Expense ID to delete")

    # update
    up_parser = subparsers.add_parser("update", help="Update an existing expense")
    up_parser.add_argument("--id", required=True, type=int, help="Expense ID to update")
    up_parser.add_argument("--description", default=None, help="New description")
    up_parser.add_argument("--amount", default=None, help="New amount")
    up_parser.add_argument("--category", default=None, help="New category")

    # set-budget
    budget_parser = subparsers.add_parser("set-budget", help="Set monthly budget")
    budget_parser.add_argument("--month", required=True, type=int, help="Month (1-12)")
    budget_parser.add_argument("--amount", required=True, help="Monthly budget amount")
    budget_parser.add_argument("--year", type=int, default=None, help="Year (default: current year)")

    # export
    export_parser = subparsers.add_parser("export", help="Export expenses to CSV")
    export_parser.add_argument("--file", default="expenses.csv", help="CSV target path (default: expenses.csv)")

    return parser


def run_cli(args: Optional[List[str]] = None, service: Optional[ExpenseService] = None) -> int:
    if service is None:
        service = get_default_service()

    parser = build_parser()
    if args is None:
        args = sys.argv[1:]

    if not args:
        parser.print_help()
        return 0

    parsed = parser.parse_args(args)

    try:
        if parsed.command == "add":
            exp_date = date.fromisoformat(parsed.date) if parsed.date else None
            res = service.add_expense(
                description=parsed.description,
                amount=parsed.amount,
                category=parsed.category,
                date_val=exp_date,
            )
            print(f"# Expense added successfully (ID: {res.expense.id})")
            if res.warning:
                print(f"[ALERT] {res.warning}")
            return 0

        elif parsed.command == "list":
            expenses = service.list_expenses(category=parsed.category)
            if not expenses:
                print("No expenses found.")
                return 0

            # Table Header
            print(f"{'# ID':<6} {'Date':<12} {'Description':<25} {'Amount':<10} {'Category':<15}")
            print("-" * 70)
            for e in expenses:
                print(f"{e.id:<6} {e.date.isoformat():<12} {e.description:<25} ${e.amount:<9.2f} {e.category:<15}")
            return 0

        elif parsed.command == "summary":
            if parsed.month is not None:
                if not (1 <= parsed.month <= 12):
                    print("Error: Month must be an integer between 1 and 12.")
                    return 1
                y = parsed.year or date.today().year
                month_name = calendar.month_name[parsed.month]
                total = service.get_summary(month=parsed.month, year=y)
                print(f"# Total expenses for {month_name}: ${total:.2f}")
            else:
                total = service.get_summary()
                print(f"# Total expenses: ${total:.2f}")
            return 0

        elif parsed.command == "delete":
            service.delete_expense(parsed.id)
            print("# Expense deleted successfully")
            return 0

        elif parsed.command == "update":
            if not any([parsed.description, parsed.amount, parsed.category]):
                print("Error: Provide at least one field to update (--description, --amount, --category).")
                return 1
            service.update_expense(
                expense_id=parsed.id,
                description=parsed.description,
                amount=parsed.amount,
                category=parsed.category,
            )
            print("# Expense updated successfully")
            return 0

        elif parsed.command == "set-budget":
            b = service.set_budget(month=parsed.month, amount=parsed.amount, year=parsed.year)
            print(f"# Budget set successfully for month {b.month}: ${b.amount:.2f}")
            return 0

        elif parsed.command == "export":
            path = service.export_to_csv(parsed.file)
            print(f"# Expenses exported to {path}")
            return 0

        else:
            parser.print_help()
            return 0

    except KeyError as e:
        print(f"Error: {e.args[0]}")
        return 1
    except ValueError as e:
        print(f"Error: {str(e)}")
        return 1
    except Exception as e:
        print(f"Error: {str(e)}")
        return 1


if __name__ == "__main__":
    sys.exit(run_cli())
