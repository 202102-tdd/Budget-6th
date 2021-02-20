import unittest
import calendar
from datetime import datetime, timedelta
from unittest import mock

from IBudgetRepo import Budget, IBudgetRepo


class BudgetCalculator(object):
    def __init__(self, budgets):
        self.budgets = budgets()
        self.budgets_mapper = {}
        for budget in self.budgets:
            self.budgets_mapper[budget.year_month] = budget.amount

    # def query2(self, start: datetime, end: datetime):
    #     if len(self.budgets) == 0:
    #         return 0
    #
    #     total_days_start = calendar.monthrange(start.year, start.month)[1]
    #     total_days_end = calendar.monthrange(end.year, end.month)[1]
    #
    #     first_rest_days = total_days_start - start.day + 1
    #     end_rest_days = end.day
    #
    #     start_year_month = datetime.strftime(start, "%Y%m")
    #     end_year_month = datetime.strftime(end, "%Y%m")
    #
    #     first_ratio_amount = first_rest_days/total_days_start * self.budgets_mapper.get(start_year_month)
    #     end_ratio_amount = end_rest_days/total_days_end * self.budgets_mapper.get(end_year_month)
    #
    #     final = first_ratio_amount + end_ratio_amount
    #
    #     if start_year_month == end_year_month:
    #         return final/2
    #
    #     return final

    def query(self, start: datetime, end: datetime):
        iterdate = start - timedelta(days=1)
        months = {}

        while iterdate < end:
            iterdate = iterdate + timedelta(days=1)
            month = datetime.strftime(iterdate, "%Y%m")
            if month in months:
                months[month][0] += 1
            else:
                month_days = calendar.monthrange(iterdate.year, iterdate.month)[1]
                months[month] = [1, month_days]

        for budget in self.budgets:
            if budget.year_month in months:
                months[budget.year_month].append(budget.amount)

        result = 0

        for m in months.values():
            if len(m) == 3:
                result += m[2]*(m[0]/m[1])

        return result


class BudgetTestCase(unittest.TestCase):
    @mock.patch('IBudgetRepo.IBudgetRepo.get_all')
    def test_full_month(self, mock_get_all):
        new_budget = Budget('202101', 310)
        mock_get_all.return_value = [new_budget]
        budget_cal = BudgetCalculator(IBudgetRepo().get_all)

        result = budget_cal.query(datetime.strptime('20210101', '%Y%m%d'), datetime.strptime('20210131', '%Y%m%d'))

        self.assertEqual(310.0, result)

    @mock.patch('IBudgetRepo.IBudgetRepo.get_all')
    def test_cross_two_months(self, mock_get_all):
        budget_Jan = Budget('202101', 310)
        budget_Feb = Budget('202102', 28)
        mock_get_all.return_value = [budget_Jan, budget_Feb]

        budget_cal = BudgetCalculator(IBudgetRepo().get_all)

        result = budget_cal.query(datetime.strptime('20210130', '%Y%m%d'), datetime.strptime('20210203', '%Y%m%d'))

        self.assertEqual(23.0, result)

    @mock.patch('IBudgetRepo.IBudgetRepo.get_all')
    def test_cross_two_months_desc(self, mock_get_all):
        budget_Jan = Budget('202101', 310)
        budget_Feb = Budget('202102', 28)
        mock_get_all.return_value = [budget_Feb, budget_Jan]

        budget_cal = BudgetCalculator(IBudgetRepo().get_all)

        result = budget_cal.query(datetime.strptime('20210130', '%Y%m%d'), datetime.strptime('20210203', '%Y%m%d'))

        self.assertEqual(23.0, result)

    @mock.patch('IBudgetRepo.IBudgetRepo.get_all')
    def test_cross_nodata(self, mock_get_all):
        mock_get_all.return_value = []
        budget_cal = BudgetCalculator(IBudgetRepo().get_all)

        result = budget_cal.query(datetime.strptime('20210130', '%Y%m%d'), datetime.strptime('20210203', '%Y%m%d'))

        self.assertEqual(0.0, result)

    @mock.patch('IBudgetRepo.IBudgetRepo.get_all')
    def test_cross_three_months(self, mock_get_all):
        budget_Jan = Budget('202101', 310)
        budget_Feb = Budget('202102', 28)
        budget_Mar = Budget('202103', 3100)

        mock_get_all.return_value = [budget_Jan, budget_Feb, budget_Mar]

        budget_cal = BudgetCalculator(IBudgetRepo().get_all)

        result = budget_cal.query(datetime.strptime('20210130', '%Y%m%d'), datetime.strptime('20210303', '%Y%m%d'))

        self.assertEqual(348.0, result)

    @mock.patch('IBudgetRepo.IBudgetRepo.get_all')
    def test_same_date(self, mock_get_all):
        new_budget = Budget('202101', 310)
        mock_get_all.return_value = [new_budget]
        budget_cal = BudgetCalculator(IBudgetRepo().get_all)

        result = budget_cal.query(datetime.strptime('20210101', '%Y%m%d'), datetime.strptime('20210101', '%Y%m%d'))

        self.assertEqual(10.0, result)

    @mock.patch('IBudgetRepo.IBudgetRepo.get_all')
    def test_cross_years(self, mock_get_all):
        budget_Dec = Budget('202012', 310)
        budget_Feb = Budget('202102', 28)
        budget_Mar = Budget('202103', 3100)

        mock_get_all.return_value = [budget_Dec, budget_Feb, budget_Mar]

        budget_cal = BudgetCalculator(IBudgetRepo().get_all)

        result = budget_cal.query(datetime.strptime('20201231', '%Y%m%d'), datetime.strptime('20210303', '%Y%m%d'))

        self.assertEqual(338.0, result)

    @mock.patch('IBudgetRepo.IBudgetRepo.get_all')
    def test_less_month(self, mock_get_all):
        budget_Dec = Budget('202012', 310)
        budget_Feb = Budget('202102', 28)
        budget_Mar = Budget('202103', 3100)

        mock_get_all.return_value = [budget_Dec, budget_Feb, budget_Mar]

        budget_cal = BudgetCalculator(IBudgetRepo().get_all)

        result = budget_cal.query(datetime.strptime('20201231', '%Y%m%d'), datetime.strptime('20210401', '%Y%m%d'))

        self.assertEqual(3138.0, result)


if __name__ == '__main__':
    unittest.main()
