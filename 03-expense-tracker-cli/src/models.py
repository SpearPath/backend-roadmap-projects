from dataclasses import dataclass, field
from datetime import datetime, date
from decimal import Decimal, ROUND_HALF_UP
from typing import Optional, Union


def to_decimal(val: Union[Decimal, float, int, str]) -> Decimal:
    """Helper to convert inputs to 2-decimal-place Decimal."""
    if isinstance(val, (float, int)):
        d = Decimal(str(val))
    elif isinstance(val, str):
        d = Decimal(val.strip())
    elif isinstance(val, Decimal):
        d = val
    else:
        raise TypeError(f"Cannot convert {type(val)} to Decimal")
    return d.quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)


@dataclass
class Expense:
    description: str
    amount: Union[Decimal, float, int, str]
    id: Optional[int] = None
    category: str = "General"
    date: Optional[Union[date, str]] = None
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None

    def __post_init__(self):
        # Validate description
        if not isinstance(self.description, str) or not self.description.strip():
            raise ValueError("Expense description cannot be empty.")
        self.description = self.description.strip()

        # Validate & quantize amount
        self.amount = to_decimal(self.amount)
        if self.amount <= Decimal("0.00"):
            raise ValueError("Expense amount must be greater than zero.")

        # Category
        if not self.category or not self.category.strip():
            self.category = "General"
        else:
            self.category = self.category.strip()

        # Date handling
        if self.date is None:
            self.date = date.today()
        elif isinstance(self.date, str):
            self.date = date.fromisoformat(self.date)

        # Timestamps
        now = datetime.now()
        if self.created_at is None:
            self.created_at = now
        if self.updated_at is None:
            self.updated_at = self.created_at


@dataclass
class Budget:
    month: int
    amount: Union[Decimal, float, int, str]
    year: Optional[int] = None

    def __post_init__(self):
        if not isinstance(self.month, int) or not (1 <= self.month <= 12):
            raise ValueError("Budget month must be an integer between 1 and 12.")

        self.amount = to_decimal(self.amount)
        if self.amount <= Decimal("0.00"):
            raise ValueError("Budget amount must be greater than zero.")

        if self.year is None:
            self.year = date.today().year
