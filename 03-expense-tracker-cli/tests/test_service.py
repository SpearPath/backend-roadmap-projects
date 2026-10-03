import unittest
from datetime import date
from decimal import Decimal
import tempfile
import csv
from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from src.models import Expense, Budget
from src.repository.sqlite_repo import SQLiteExpenseRepository
from src.expense_service import ExpenseService


class TestExpenseService(unittest.TestCase):
    def setUp(self):
        self.repo = SQLiteExpenseRepository(db_path=":memory:")
        self.service = ExpenseService(repository=self.repo)

    def tearDown(self):
        self.repo.close()

    def test_add_expense_without_budget_warning(self):
        result = self.service.add_expense(
            description="Lunch",
            amount="15.50",
            category="Food",
            date_val=date(2026, 10, 1)
        )
        self.assertIsNotNone(result.expense.id)
        self.assertEqual(result.expense.amount, Decimal("15.50"))
        self.assertIsNone(result.warning)

    def test_add_expense_triggers_budget_warning_when_exceeded(self):
        # Set budget of $50 for Oct 2026
        self.service.set_budget(month=10, year=2026, amount="50.00")

        # Add $30 expense -> within budget
        r1 = self.service.add_expense("Groceries", "30.00", date_val=date(2026, 10, 2))
        self.assertIsNone(r1.warning)

        # Add $25 expense -> total $55, exceeds $50 budget
        r2 = self.service.add_expense("Dinner", "25.00", date_val=date(2026, 10, 3))
        self.assertIsNotNone(r2.warning)
        self.assertIn("exceeded", r2.warning.lower())
        self.assertIn("50.00", r2.warning)

    def test_update_expense_success(self):
        r = self.service.add_expense("Coffee", "4.00")
        updated = self.service.update_expense(r.expense.id, description="Latte", amount="5.50")
        self.assertEqual(updated.description, "Latte")
        self.assertEqual(updated.amount, Decimal("5.50"))

    def test_update_nonexistent_expense_raises_key_error(self):
        with self.assertRaises(KeyError):
            self.service.update_expense(999, description="Phantom")

    def test_delete_expense_success(self):
        r = self.service.add_expense("Snack", "3.00")
        deleted = self.service.delete_expense(r.expense.id)
        self.assertTrue(deleted)

    def test_delete_nonexistent_expense_raises_key_error(self):
        with self.assertRaises(KeyError):
            self.service.delete_expense(999)

    def test_export_to_csv(self):
        self.service.add_expense("Groceries", "45.00", category="Food", date_val=date(2026, 10, 1))
        self.service.add_expense("Bus ticket", "2.75", category="Transport", date_val=date(2026, 10, 2))

        with tempfile.TemporaryDirectory() as tmpdir:
            csv_path = Path(tmpdir) / "expenses.csv"
            self.service.export_to_csv(csv_path)

            self.assertTrue(csv_path.exists())
            with open(csv_path, "r", encoding="utf-8") as f:
                reader = csv.reader(f)
                rows = list(reader)

            self.assertEqual(rows[0], ["ID", "Date", "Description", "Amount", "Category"])
            self.assertEqual(len(rows), 3)  # header + 2 expenses
            self.assertEqual(rows[1][2], "Groceries")
            self.assertEqual(rows[1][3], "45.00")
            self.assertEqual(rows[2][2], "Bus ticket")
            self.assertEqual(rows[2][3], "2.75")


if __name__ == "__main__":
    unittest.main()
