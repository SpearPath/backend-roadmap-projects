from datetime import datetime, date
from decimal import Decimal
from typing import Optional, Union, List

from src.models import Expense, Budget, to_decimal
from src.repository.base import ExpenseRepository


class PostgreSQLExpenseRepository(ExpenseRepository):
    """
    PostgreSQL persistence repository.
    Supports either psycopg (v3) or psycopg2 (v2).
    """

    def __init__(self, connection_url: str):
        self.connection_url = connection_url
        self._driver = None
        self._conn = None
        self._connect()
        self._init_db()

    def _connect(self):
        try:
            import psycopg
            self._driver = "psycopg"
            self._conn = psycopg.connect(self.connection_url)
        except ImportError:
            try:
                import psycopg2
                import psycopg2.extras
                self._driver = "psycopg2"
                self._conn = psycopg2.connect(self.connection_url)
            except ImportError:
                raise ImportError(
                    "PostgreSQL driver not found. Please install psycopg with:\n"
                    "    pip install psycopg[binary]  OR  pip install psycopg2-binary"
                )

    def _init_db(self) -> None:
        with self._conn.cursor() as cur:
            cur.execute(
                """
                CREATE TABLE IF NOT EXISTS expenses (
                    id SERIAL PRIMARY KEY,
                    description TEXT NOT NULL,
                    amount NUMERIC(12, 2) NOT NULL,
                    category VARCHAR(100) NOT NULL DEFAULT 'General',
                    expense_date DATE NOT NULL,
                    created_at TIMESTAMP NOT NULL,
                    updated_at TIMESTAMP NOT NULL
                );
                """
            )
            cur.execute(
                """
                CREATE TABLE IF NOT EXISTS budgets (
                    month INT NOT NULL,
                    year INT NOT NULL,
                    amount NUMERIC(12, 2) NOT NULL,
                    PRIMARY KEY (month, year)
                );
                """
            )
            self._conn.commit()

    def add_expense(self, expense: Expense) -> Expense:
        with self._conn.cursor() as cur:
            cur.execute(
                """
                INSERT INTO expenses (description, amount, category, expense_date, created_at, updated_at)
                VALUES (%s, %s, %s, %s, %s, %s)
                RETURNING id;
                """,
                (
                    expense.description,
                    expense.amount,
                    expense.category,
                    expense.date,
                    expense.created_at,
                    expense.updated_at,
                ),
            )
            new_id = cur.fetchone()[0]
            expense.id = new_id
            self._conn.commit()
        return expense

    def get_expense(self, expense_id: int) -> Optional[Expense]:
        with self._conn.cursor() as cur:
            cur.execute(
                "SELECT id, description, amount, category, expense_date, created_at, updated_at FROM expenses WHERE id = %s",
                (expense_id,),
            )
            row = cur.fetchone()
            if not row:
                return None
            return Expense(
                id=row[0],
                description=row[1],
                amount=to_decimal(row[2]),
                category=row[3],
                date=row[4] if isinstance(row[4], date) else date.fromisoformat(str(row[4])),
                created_at=row[5],
                updated_at=row[6],
            )

    def list_expenses(self, category: Optional[str] = None) -> List[Expense]:
        with self._conn.cursor() as cur:
            if category:
                cur.execute(
                    "SELECT id, description, amount, category, expense_date, created_at, updated_at "
                    "FROM expenses WHERE LOWER(category) = LOWER(%s) ORDER BY expense_date DESC, id DESC",
                    (category.strip(),),
                )
            else:
                cur.execute(
                    "SELECT id, description, amount, category, expense_date, created_at, updated_at "
                    "FROM expenses ORDER BY expense_date DESC, id DESC"
                )
            rows = cur.fetchall()

        expenses = []
        for r in rows:
            expenses.append(
                Expense(
                    id=r[0],
                    description=r[1],
                    amount=to_decimal(r[2]),
                    category=r[3],
                    date=r[4] if isinstance(r[4], date) else date.fromisoformat(str(r[4])),
                    created_at=r[5],
                    updated_at=r[6],
                )
            )
        return expenses

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

        with self._conn.cursor() as cur:
            cur.execute(
                """
                UPDATE expenses
                SET description = %s, amount = %s, category = %s, expense_date = %s, updated_at = %s
                WHERE id = %s
                """,
                (new_desc, new_amount, new_cat, new_date, now, expense_id),
            )
            self._conn.commit()

        return self.get_expense(expense_id)

    def delete_expense(self, expense_id: int) -> bool:
        with self._conn.cursor() as cur:
            cur.execute("DELETE FROM expenses WHERE id = %s", (expense_id,))
            deleted = cur.rowcount > 0
            self._conn.commit()
            return deleted

    def get_summary(
        self, month: Optional[int] = None, year: Optional[int] = None
    ) -> Decimal:
        query = "SELECT COALESCE(SUM(amount), 0) FROM expenses WHERE 1=1"
        params = []
        if month is not None:
            query += " AND EXTRACT(MONTH FROM expense_date) = %s"
            params.append(month)
        if year is not None:
            query += " AND EXTRACT(YEAR FROM expense_date) = %s"
            params.append(year)

        with self._conn.cursor() as cur:
            cur.execute(query, tuple(params))
            row = cur.fetchone()
            return to_decimal(row[0]) if row else Decimal("0.00")

    def set_budget(self, budget: Budget) -> None:
        with self._conn.cursor() as cur:
            cur.execute(
                """
                INSERT INTO budgets (month, year, amount)
                VALUES (%s, %s, %s)
                ON CONFLICT (month, year) DO UPDATE SET amount = EXCLUDED.amount;
                """,
                (budget.month, budget.year, budget.amount),
            )
            self._conn.commit()

    def get_budget(self, month: int, year: int) -> Optional[Budget]:
        with self._conn.cursor() as cur:
            cur.execute(
                "SELECT month, year, amount FROM budgets WHERE month = %s AND year = %s",
                (month, year),
            )
            row = cur.fetchone()
            if not row:
                return None
            return Budget(month=row[0], year=row[1], amount=to_decimal(row[2]))

    def close(self) -> None:
        if self._conn:
            self._conn.close()
