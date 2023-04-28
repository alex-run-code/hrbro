# Create your tests here.
from django.test import TestCase
from rest_framework.test import APIClient
from django.urls import reverse
from datetime import date

from .models import Employee, Industry
from .views import get_age


class GeneralStatisticTestCase(TestCase):

    def setUp(self):
        self.client = APIClient()

        # Create sample employee data for testing
        self.industry_1 = Industry.objects.create(name='Industry 1')
        self.industry_2 = Industry.objects.create(name='Industry 2')

        Employee.objects.create(
            first_name='John', last_name='Doe', email='john.doe@example.com',
            gender='M', date_of_birth=date(1990, 1, 1), salary=50000,
            years_of_experience=5, industry=self.industry_1
        )
        Employee.objects.create(
            first_name='Jane', last_name='Doe', email='jane.doe@example.com',
            gender='F', date_of_birth=date(1985, 1, 1), salary=60000,
            years_of_experience=8, industry=self.industry_1
        )
        Employee.objects.create(
            first_name='Bob', last_name='Smith', email='bob.smith@example.com',
            gender='M', date_of_birth=date(1980, 1, 1), salary=70000,
            years_of_experience=10, industry=self.industry_2
        )

    def test_general_statistic_api_view(self):
        url = reverse('averages_per_industry')
        response = self.client.get(url)

        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.data), 2)

        # Check that the data is sorted by salary in descending order
        self.assertGreater(response.data[0]['salary'], response.data[1]['salary'])

        # Check that the average years of experience is calculated correctly
        self.assertEqual(response.data[0]['years_of_experience'], 10.0)
        self.assertEqual(response.data[1]['years_of_experience'], 6.5)

        # Check that the age is calculated correctly
        # Ages can't be hardcoded because they change every day :)
        dob_of_employees_industry_1 = Employee.objects\
            .filter(industry=self.industry_1)\
            .values_list('date_of_birth')
        ei1_ages = list(map(get_age, [age[0] for age in dob_of_employees_industry_1]))
        avg_ei1_ages = sum(ei1_ages) / len(ei1_ages)

        dob_of_employees_industry_2 = Employee.objects \
            .filter(industry=self.industry_2) \
            .values_list('date_of_birth')
        ei2_ages = list(map(get_age, [age[0] for age in dob_of_employees_industry_2]))
        avg_ei2_ages = sum(ei2_ages) / len(ei2_ages)

        self.assertEqual(response.data[0]['age'], avg_ei2_ages)
        self.assertEqual(response.data[1]['age'], avg_ei1_ages)

        # Check that the industry names are correct
        self.assertEqual(response.data[0]['industry'], 'Industry 2')
        self.assertEqual(response.data[1]['industry'], 'Industry 1')

        # Check that the average salary is calculated correctly
        self.assertEqual(response.data[0]['salary'], 70000.0)
        self.assertEqual(response.data[1]['salary'], 55000.0)
