import unittest
from unittest.mock import patch
import io
import sys
from pathlib import Path
from decimal import Decimal

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from src.repository.sqlite_repo import SQLiteExpenseRepository
from src.expense_service import ExpenseService
from src.cli import run_cli


class TestCLI(unittest.TestCase):
    def setUp(self):
        self.repo = SQLiteExpenseRepository(db_path=":memory:")
        self.service = ExpenseService(repository=self.repo)

    def tearDown(self):
        self.repo.close()

    def execute_cli(self, args: list[str]) -> tuple[int, str]:
        stdout = io.StringIO()
        with patch("sys.stdout", stdout):
            code = run_cli(args, service=self.service)
        return code, stdout.getvalue()

    def test_cli_add_expense(self):
        code, output = self.execute_cli(["add", "--description", "Lunch", "--amount", "20.00"])
        self.assertEqual(code, 0)
        self.assertIn("Expense added successfully", output)
        self.assertIn("ID: 1", output)

    def test_cli_add_expense_with_category(self):
        code, output = self.execute_cli(["add", "--description", "Train", "--amount", "5.50", "--category", "Transport"])
        self.assertEqual(code, 0)
        self.assertIn("Expense added successfully", output)

    def test_cli_list_expenses(self):
        self.execute_cli(["add", "--description", "Coffee", "--amount", "4.00"])
        self.execute_cli(["add", "--description", "Sandwich", "--amount", "8.50"])

        code, output = self.execute_cli(["list"])
        self.assertEqual(code, 0)
        self.assertIn("Coffee", output)
        self.assertIn("Sandwich", output)
        self.assertIn("ID", output)
        self.assertIn("Amount", output)

    def test_cli_summary(self):
        self.execute_cli(["add", "--description", "Coffee", "--amount", "4.00"])
        self.execute_cli(["add", "--description", "Sandwich", "--amount", "8.50"])

        code, output = self.execute_cli(["summary"])
        self.assertEqual(code, 0)
        self.assertIn("Total expenses", output)
        self.assertIn("$12.50", output)

    def test_cli_delete_expense(self):
        self.execute_cli(["add", "--description", "Snack", "--amount", "3.00"])
        code, output = self.execute_cli(["delete", "--id", "1"])
        self.assertEqual(code, 0)
        self.assertIn("Expense deleted successfully", output)

    def test_cli_delete_nonexistent_returns_error(self):
        code, output = self.execute_cli(["delete", "--id", "999"])
        self.assertNotEqual(code, 0)
        self.assertIn("not found", output.lower())

    def test_cli_update_expense(self):
        self.execute_cli(["add", "--description", "Old", "--amount", "10.00"])
        code, output = self.execute_cli(["update", "--id", "1", "--description", "New Dinner", "--amount", "15.00"])
        self.assertEqual(code, 0)
        self.assertIn("Expense updated successfully", output)

    def test_cli_set_budget(self):
        code, output = self.execute_cli(["set-budget", "--month", "10", "--amount", "500"])
        self.assertEqual(code, 0)
        self.assertIn("Budget set successfully", output)


if __name__ == "__main__":
    unittest.main()
