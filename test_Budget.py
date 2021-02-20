import unittest
import calendar
from datetime import datetime
from unittest import mock

from IBudgetRepo import Budget, IBudgetRepo


class BudgetCalculator(object):
    def __init__(self, budgets):
        self.budgets = budgets()
        self.budgets_mapper = {}
        for budget in self.budgets:
            self.budgets_mapper[budget.year_month] = budget.amount

    def query(self, start: datetime, end: datetime):
        budget_datetime = datetime.strptime(self.budgets[0].year_month, '%Y%m')

        if start.month == end.month == budget_datetime.month:
            return self.budgets[0].amount

        total_days_start = calendar.monthrange(start.year, start.month)[1]
        total_days_end = calendar.monthrange(end.year, end.month)[1]

        first_rest_days = total_days_start - start.day + 1
        end_rest_days = end.day

        first_ratio_amount = first_rest_days/total_days_start * self.budgets_mapper.get(datetime.strftime(start, "%Y%m"))
        end_ratio_amount = end_rest_days/total_days_end * self.budgets_mapper.get(datetime.strftime(end, "%Y%m"))

        return first_ratio_amount + end_ratio_amount


class BudgetTestCase(unittest.TestCase):
    @mock.patch('IBudgetRepo.IBudgetRepo.get_all')
    def test_full_month(self, mock_get_all):
        new_budget = Budget('202101', 310)
        mock_get_all.return_value = [new_budget]
        budget_cal = BudgetCalculator(IBudgetRepo().get_all)

        result = budget_cal.query(datetime.strptime('20210101', '%Y%m%d'), datetime.strptime('20210131', '%Y%m%d'))

        self.assertEqual(310, result)

    @mock.patch('IBudgetRepo.IBudgetRepo.get_all')
    def test_cross_month(self, mock_get_all):
        budget_Jan = Budget('202101', 310)
        budget_Feb = Budget('202102', 28)
        mock_get_all.return_value = [budget_Jan, budget_Feb]

        budget_cal = BudgetCalculator(IBudgetRepo().get_all)

        result = budget_cal.query(datetime.strptime('20210130', '%Y%m%d'), datetime.strptime('20210203', '%Y%m%d'))

        self.assertEqual(23, result)


if __name__ == '__main__':
    unittest.main()
