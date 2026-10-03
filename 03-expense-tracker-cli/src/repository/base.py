from abc import ABC, abstractmethod
from datetime import date
from decimal import Decimal
from typing import Optional, Union, List
from src.models import Expense, Budget


class ExpenseRepository(ABC):
    @abstractmethod
    def add_expense(self, expense: Expense) -> Expense:
        """Persist a new expense and assign an ID."""
        pass

    @abstractmethod
    def get_expense(self, expense_id: int) -> Optional[Expense]:
        """Retrieve an expense by its ID."""
        pass

    @abstractmethod
    def list_expenses(self, category: Optional[str] = None) -> List[Expense]:
        """List expenses, optionally filtered by category."""
        pass

    @abstractmethod
    def update_expense(
        self,
        expense_id: int,
        description: Optional[str] = None,
        amount: Optional[Union[Decimal, str, float]] = None,
        category: Optional[str] = None,
        date_val: Optional[date] = None,
    ) -> Optional[Expense]:
        """Update an existing expense's fields."""
        pass

    @abstractmethod
    def delete_expense(self, expense_id: int) -> bool:
        """Delete an expense by ID. Returns True if deleted, False if not found."""
        pass

    @abstractmethod
    def get_summary(
        self, month: Optional[int] = None, year: Optional[int] = None
    ) -> Decimal:
        """Return the sum of expenses, optionally filtered by month and year."""
        pass

    @abstractmethod
    def set_budget(self, budget: Budget) -> None:
        """Create or update a budget for a given month and year."""
        pass

    @abstractmethod
    def get_budget(self, month: int, year: int) -> Optional[Budget]:
        """Retrieve the budget for a specific month and year."""
        pass

    @abstractmethod
    def close(self) -> None:
        """Close connection or free resources."""
        pass
