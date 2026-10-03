import sqlite3
from datetime import datetime, date
from decimal import Decimal
from typing import Optional, Union, List
from pathlib import Path

from src.models import Expense, Budget, to_decimal
from src.repository.base import ExpenseRepository


class SQLiteExpenseRepository(ExpenseRepository):
    def __init__(self, db_path: Union[str, Path] = "expenses.db"):
        self.db_path = str(db_path)
        self.conn = sqlite3.connect(self.db_path, check_same_thread=False)
        self.conn.row_factory = sqlite3.Row
        self._init_db()

    def _init_db(self) -> None:
        with self.conn:
            self.conn.execute(
                """
                CREATE TABLE IF NOT EXISTS expenses (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    description TEXT NOT NULL,
                    amount TEXT NOT NULL,
                    category TEXT NOT NULL DEFAULT 'General',
                    expense_date TEXT NOT NULL,
                    created_at TEXT NOT NULL,
                    updated_at TEXT NOT NULL
                );
                """
            )
            self.conn.execute(
                """
                CREATE TABLE IF NOT EXISTS budgets (
                    month INTEGER NOT NULL,
                    year INTEGER NOT NULL,
                    amount TEXT NOT NULL,
                    PRIMARY KEY (month, year)
                );
                """
            )

    def _row_to_expense(self, row: sqlite3.Row) -> Expense:
        return Expense(
            id=row["id"],
            description=row["description"],
            amount=Decimal(row["amount"]),
            category=row["category"],
            date=date.fromisoformat(row["expense_date"]),
            created_at=datetime.fromisoformat(row["created_at"]),
            updated_at=datetime.fromisoformat(row["updated_at"]),
        )

    def add_expense(self, expense: Expense) -> Expense:
        with self.conn:
            cursor = self.conn.execute(
                """
                INSERT INTO expenses (description, amount, category, expense_date, created_at, updated_at)
                VALUES (?, ?, ?, ?, ?, ?)
                """,
                (
                    expense.description,
                    str(expense.amount),
                    expense.category,
                    expense.date.isoformat(),
                    expense.created_at.isoformat(),
                    expense.updated_at.isoformat(),
                ),
            )
            expense.id = cursor.lastrowid
        return expense

    def get_expense(self, expense_id: int) -> Optional[Expense]:
        cursor = self.conn.execute(
            "SELECT * FROM expenses WHERE id = ?", (expense_id,)
        )
        row = cursor.fetchone()
        return self._row_to_expense(row) if row else None

    def list_expenses(self, category: Optional[str] = None) -> List[Expense]:
        if category:
            cursor = self.conn.execute(
                "SELECT * FROM expenses WHERE LOWER(category) = LOWER(?) ORDER BY expense_date DESC, id DESC",
                (category.strip(),),
            )
        else:
            cursor = self.conn.execute(
                "SELECT * FROM expenses ORDER BY expense_date DESC, id DESC"
            )
        return [self._row_to_expense(r) for r in cursor.fetchall()]

    def update_expense(
        self,
        expense_id: int,
        description: Optional[str] = None,
        amount: Optional[Union[Decimal, str, float]] = None,
        category: Optional[str] = None,
        date_val: Optional[date] = None,
    ) -> Optional[Expense]:
        existing = self.get_expense(expense_id)
        if not existing:
            return None

        new_desc = description.strip() if description is not None else existing.description
        new_amount = to_decimal(amount) if amount is not None else existing.amount
        new_cat = category.strip() if category is not None else existing.category
        new_date = date_val if date_val is not None else existing.date
        now = datetime.now()

        with self.conn:
            self.conn.execute(
                """
                UPDATE expenses
                SET description = ?, amount = ?, category = ?, expense_date = ?, updated_at = ?
                WHERE id = ?
                """,
                (
                    new_desc,
                    str(new_amount),
                    new_cat,
                    new_date.isoformat(),
                    now.isoformat(),
                    expense_id,
                ),
            )

        return self.get_expense(expense_id)

    def delete_expense(self, expense_id: int) -> bool:
        with self.conn:
            cursor = self.conn.execute(
                "DELETE FROM expenses WHERE id = ?", (expense_id,)
            )
            return cursor.rowcount > 0

    def get_summary(
        self, month: Optional[int] = None, year: Optional[int] = None
    ) -> Decimal:
        query = "SELECT amount, expense_date FROM expenses"
        cursor = self.conn.execute(query)
        rows = cursor.fetchall()

        total = Decimal("0.00")
        for row in rows:
            exp_date = date.fromisoformat(row["expense_date"])
            if month is not None and exp_date.month != month:
                continue
            if year is not None and exp_date.year != year:
                continue
            total += Decimal(row["amount"])

        return to_decimal(total)

    def set_budget(self, budget: Budget) -> None:
        with self.conn:
            self.conn.execute(
                """
                INSERT INTO budgets (month, year, amount)
                VALUES (?, ?, ?)
                ON CONFLICT(month, year) DO UPDATE SET amount = excluded.amount
                """,
                (budget.month, budget.year, str(budget.amount)),
            )

    def get_budget(self, month: int, year: int) -> Optional[Budget]:
        cursor = self.conn.execute(
            "SELECT * FROM budgets WHERE month = ? AND year = ?",
            (month, year),
        )
        row = cursor.fetchone()
        if not row:
            return None
        return Budget(month=row["month"], year=row["year"], amount=Decimal(row["amount"]))

    def close(self) -> None:
        self.conn.close()
