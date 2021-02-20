from dataclasses import dataclass


class IBudgetRepo:
    def __init__(self):
        self.budget = []

    def get_all(self):
        return self.budget


@dataclass
class Budget:
    year_month: str
    amount: int
