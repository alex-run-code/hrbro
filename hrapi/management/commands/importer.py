from django.core.management.base import BaseCommand
import pandas as pd
from hrapi.models import Employee, Industry
from datetime import datetime
from django.db import IntegrityError
import math


class Command(BaseCommand):
    help = "Import mock data in the database"

    def add_arguments(self, parser):
        parser.add_argument('file_path', type=str, help='File path to process')

    def format_date(self, date):
        date_obj = datetime.strptime(date, '%d/%m/%Y')
        formatted_date = date_obj.strftime('%Y-%m-%d')
        return formatted_date

    def handle(self, *args, **options):
        # what if a field is missing ?
        # what if we try to insert a duplicate ?
        df = pd.read_json(options['file_path'])
        df = df.where(pd.notnull(df), None)
        for index, employee in df.iterrows():

            if employee['industry']:
                industry, _ = Industry.objects.get_or_create(
                    name=employee['industry']
                )
            else:
                industry = None

            try:
                salary = employee['salary'] if not math.isnan(
                    employee['salary']) else None
                yoe = employee['years_of_experience'] if not math.isnan(
                    employee['years_of_experience']) else None
                Employee.objects.create(
                    first_name=employee['first_name'],
                    last_name=employee['last_name'],
                    email=employee['email'],
                    gender=employee['gender'],
                    date_of_birth=self.format_date(employee['date_of_birth']),
                    industry=industry,
                    salary=salary,
                    years_of_experience=yoe,
                )
                print(f"Successfully added {employee['first_name']} - {index}/{len(df)}")
            except IntegrityError:
                print(f"Couldn't add {employee['first_name']}, email already taken: {employee['email']} - {index}/{len(df)}")


