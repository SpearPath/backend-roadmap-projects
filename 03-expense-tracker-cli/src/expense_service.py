import csv
from dataclasses import dataclass
from datetime import date
from decimal import Decimal
from pathlib import Path
from typing import Optional, Union, List

from src.models import Expense, Budget, to_decimal
from src.repository.base import ExpenseRepository


@dataclass
class AddResult:
    expense: Expense
    warning: Optional[str] = None


class ExpenseService:
    def __init__(self, repository: ExpenseRepository):
        self.repository = repository

    def add_expense(
        self,
        description: str,
        amount: Union[Decimal, str, float],
        category: Optional[str] = None,
        date_val: Optional[date] = None,
    ) -> AddResult:
        expense = Expense(
            description=description,
            amount=amount,
            category=category or "General",
            date=date_val,
        )
        saved = self.repository.add_expense(expense)

        # Check monthly budget alert
        exp_date = saved.date
        budget = self.repository.get_budget(exp_date.month, exp_date.year)
        warning = None

        if budget is not None:
            current_month_total = self.repository.get_summary(
                month=exp_date.month, year=exp_date.year
            )
            if current_month_total > budget.amount:
                month_name = exp_date.strftime("%B")
                warning = (
                    f"Warning: You have exceeded your monthly budget of "
                    f"${budget.amount:.2f} for {month_name} {exp_date.year}! "
                    f"Current total spent: ${current_month_total:.2f}"
                )

        return AddResult(expense=saved, warning=warning)

    def list_expenses(self, category: Optional[str] = None) -> List[Expense]:
        return self.repository.list_expenses(category=category)

    def update_expense(
        self,
        expense_id: int,
        description: Optional[str] = None,
        amount: Optional[Union[Decimal, str, float]] = None,
        category: Optional[str] = None,
        date_val: Optional[date] = None,
    ) -> Expense:
        updated = self.repository.update_expense(
            expense_id=expense_id,
            description=description,
            amount=amount,
            category=category,
            date_val=date_val,
        )
        if not updated:
            raise KeyError(f"Expense with ID {expense_id} not found.")
        return updated

    def delete_expense(self, expense_id: int) -> bool:
        deleted = self.repository.delete_expense(expense_id)
        if not deleted:
            raise KeyError(f"Expense with ID {expense_id} not found.")
        return True

    def get_summary(
        self, month: Optional[int] = None, year: Optional[int] = None
    ) -> Decimal:
        return self.repository.get_summary(month=month, year=year)

    def set_budget(
        self,
        month: int,
        amount: Union[Decimal, str, float],
        year: Optional[int] = None,
    ) -> Budget:
        budget = Budget(month=month, amount=amount, year=year)
        self.repository.set_budget(budget)
        return budget

    def get_budget(self, month: int, year: Optional[int] = None) -> Optional[Budget]:
        y = year or date.today().year
        return self.repository.get_budget(month, y)

    def export_to_csv(self, filepath: Union[str, Path]) -> Path:
        out_path = Path(filepath)
        out_path.parent.mkdir(parents=True, exist_ok=True)

        expenses = sorted(
            self.repository.list_expenses(), key=lambda e: (e.date, e.id or 0)
        )
        with open(out_path, mode="w", newline="", encoding="utf-8") as f:
            writer = csv.writer(f)
            writer.writerow(["ID", "Date", "Description", "Amount", "Category"])
            for exp in expenses:
                writer.writerow(
                    [
                        exp.id,
                        exp.date.isoformat(),
                        exp.description,
                        f"{exp.amount:.2f}",
                        exp.category,
                    ]
                )
        return out_path
