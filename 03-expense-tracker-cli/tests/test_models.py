import unittest
from datetime import datetime, date
from decimal import Decimal
import sys
from pathlib import Path

# Ensure src is on sys.path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from src.models import Expense, Budget


class TestExpenseModel(unittest.TestCase):
    def test_valid_expense_creation(self):
        expense = Expense(
            id=1,
            description="Groceries",
            amount=Decimal("45.50"),
            category="Food",
            date=date(2026, 10, 3)
        )
        self.assertEqual(expense.id, 1)
        self.assertEqual(expense.description, "Groceries")
        self.assertEqual(expense.amount, Decimal("45.50"))
        self.assertEqual(expense.category, "Food")
        self.assertEqual(expense.date, date(2026, 10, 3))

    def test_amount_conversion_from_string_or_float(self):
        exp1 = Expense(description="Coffee", amount="4.75")
        self.assertEqual(exp1.amount, Decimal("4.75"))

        exp2 = Expense(description="Coffee", amount=5)
        self.assertEqual(exp2.amount, Decimal("5.00"))

    def test_amount_rounding_to_two_decimal_places(self):
        exp = Expense(description="Gas", amount=Decimal("20.123"))
        self.assertEqual(exp.amount, Decimal("20.12"))

    def test_negative_or_zero_amount_raises_error(self):
        with self.assertRaises(ValueError):
            Expense(description="Invalid", amount=Decimal("-10.00"))

        with self.assertRaises(ValueError):
            Expense(description="Invalid", amount=Decimal("0.00"))

    def test_empty_description_raises_error(self):
        with self.assertRaises(ValueError):
            Expense(description="", amount=Decimal("10.00"))

        with self.assertRaises(ValueError):
            Expense(description="   ", amount=Decimal("10.00"))

    def test_default_category_and_date(self):
        exp = Expense(description="Book", amount=Decimal("15.00"))
        self.assertEqual(exp.category, "General")
        self.assertIsInstance(exp.date, date)


class TestBudgetModel(unittest.TestCase):
    def test_valid_budget_creation(self):
        budget = Budget(month=10, year=2026, amount=Decimal("500.00"))
        self.assertEqual(budget.month, 10)
        self.assertEqual(budget.year, 2026)
        self.assertEqual(budget.amount, Decimal("500.00"))

    def test_invalid_month_raises_error(self):
        with self.assertRaises(ValueError):
            Budget(month=0, year=2026, amount=Decimal("500.00"))

        with self.assertRaises(ValueError):
            Budget(month=13, year=2026, amount=Decimal("500.00"))

    def test_negative_or_zero_budget_raises_error(self):
        with self.assertRaises(ValueError):
            Budget(month=5, year=2026, amount=Decimal("-50.00"))

        with self.assertRaises(ValueError):
            Budget(month=5, year=2026, amount=Decimal("0.00"))


if __name__ == "__main__":
    unittest.main()
