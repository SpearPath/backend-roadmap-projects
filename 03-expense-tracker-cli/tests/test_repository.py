import unittest
from datetime import date
from decimal import Decimal
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from src.models import Expense, Budget
from src.repository.sqlite_repo import SQLiteExpenseRepository


class TestSQLiteExpenseRepository(unittest.TestCase):
    def setUp(self):
        # Use an in-memory SQLite database for test isolation
        self.repo = SQLiteExpenseRepository(db_path=":memory:")

    def tearDown(self):
        self.repo.close()

    def test_add_and_get_expense(self):
        new_exp = Expense(
            description="Lunch with team",
            amount=Decimal("25.50"),
            category="Food",
            date=date(2026, 10, 1)
        )
        saved = self.repo.add_expense(new_exp)
        self.assertIsNotNone(saved.id)
        self.assertEqual(saved.id, 1)

        fetched = self.repo.get_expense(saved.id)
        self.assertIsNotNone(fetched)
        self.assertEqual(fetched.description, "Lunch with team")
        self.assertEqual(fetched.amount, Decimal("25.50"))
        self.assertEqual(fetched.category, "Food")
        self.assertEqual(fetched.date, date(2026, 10, 1))

    def test_get_nonexistent_expense_returns_none(self):
        self.assertIsNone(self.repo.get_expense(999))

    def test_list_all_expenses(self):
        self.repo.add_expense(Expense(description="Coffee", amount=Decimal("4.00"), category="Food"))
        self.repo.add_expense(Expense(description="Subway pass", amount=Decimal("20.00"), category="Transport"))

        all_expenses = self.repo.list_expenses()
        self.assertEqual(len(all_expenses), 2)
        descriptions = [e.description for e in all_expenses]
        self.assertIn("Coffee", descriptions)
        self.assertIn("Subway pass", descriptions)

    def test_list_expenses_filtered_by_category(self):
        self.repo.add_expense(Expense(description="Coffee", amount=Decimal("4.00"), category="Food"))
        self.repo.add_expense(Expense(description="Dinner", amount=Decimal("35.00"), category="Food"))
        self.repo.add_expense(Expense(description="Book", amount=Decimal("15.00"), category="Entertainment"))

        food_expenses = self.repo.list_expenses(category="Food")
        self.assertEqual(len(food_expenses), 2)
        for exp in food_expenses:
            self.assertEqual(exp.category, "Food")

    def test_update_expense(self):
        saved = self.repo.add_expense(Expense(description="Old Lunch", amount=Decimal("12.00"), category="Food"))

        updated = self.repo.update_expense(
            expense_id=saved.id,
            description="Updated Steak Dinner",
            amount=Decimal("45.00"),
            category="Dining"
        )
        self.assertIsNotNone(updated)
        self.assertEqual(updated.description, "Updated Steak Dinner")
        self.assertEqual(updated.amount, Decimal("45.00"))
        self.assertEqual(updated.category, "Dining")

        refetched = self.repo.get_expense(saved.id)
        self.assertEqual(refetched.description, "Updated Steak Dinner")
        self.assertEqual(refetched.amount, Decimal("45.00"))

    def test_update_nonexistent_expense_returns_none(self):
        result = self.repo.update_expense(999, description="Ghost", amount=Decimal("10.00"))
        self.assertIsNone(result)

    def test_delete_expense(self):
        saved = self.repo.add_expense(Expense(description="To delete", amount=Decimal("5.00")))
        deleted = self.repo.delete_expense(saved.id)
        self.assertTrue(deleted)
        self.assertIsNone(self.repo.get_expense(saved.id))

    def test_delete_nonexistent_expense_returns_false(self):
        deleted = self.repo.delete_expense(999)
        self.assertFalse(deleted)

    def test_summary_all_expenses(self):
        self.repo.add_expense(Expense(description="Item 1", amount=Decimal("10.50")))
        self.repo.add_expense(Expense(description="Item 2", amount=Decimal("20.25")))
        self.repo.add_expense(Expense(description="Item 3", amount=Decimal("5.25")))

        total = self.repo.get_summary()
        self.assertEqual(total, Decimal("36.00"))

    def test_summary_empty_expenses_returns_zero(self):
        self.assertEqual(self.repo.get_summary(), Decimal("0.00"))

    def test_summary_filtered_by_month_and_year(self):
        self.repo.add_expense(Expense(description="Oct 1", amount=Decimal("30.00"), date=date(2026, 10, 1)))
        self.repo.add_expense(Expense(description="Oct 15", amount=Decimal("20.00"), date=date(2026, 10, 15)))
        self.repo.add_expense(Expense(description="Nov 1", amount=Decimal("50.00"), date=date(2026, 11, 1)))
        self.repo.add_expense(Expense(description="Oct Prev Year", amount=Decimal("100.00"), date=date(2025, 10, 1)))

        oct_2026_total = self.repo.get_summary(month=10, year=2026)
        self.assertEqual(oct_2026_total, Decimal("50.00"))

        nov_2026_total = self.repo.get_summary(month=11, year=2026)
        self.assertEqual(nov_2026_total, Decimal("50.00"))

        dec_2026_total = self.repo.get_summary(month=12, year=2026)
        self.assertEqual(dec_2026_total, Decimal("0.00"))

    def test_set_and_get_budget(self):
        budget = Budget(month=10, year=2026, amount=Decimal("500.00"))
        self.repo.set_budget(budget)

        retrieved = self.repo.get_budget(month=10, year=2026)
        self.assertIsNotNone(retrieved)
        self.assertEqual(retrieved.amount, Decimal("500.00"))

        # Updating existing budget replaces it
        updated_budget = Budget(month=10, year=2026, amount=Decimal("600.00"))
        self.repo.set_budget(updated_budget)
        retrieved_updated = self.repo.get_budget(month=10, year=2026)
        self.assertEqual(retrieved_updated.amount, Decimal("600.00"))

    def test_get_nonexistent_budget_returns_none(self):
        self.assertIsNone(self.repo.get_budget(month=1, year=2026))


if __name__ == "__main__":
    unittest.main()
