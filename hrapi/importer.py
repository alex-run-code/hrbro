import pandas as pd
from models import Employee, Industry

df = pd.read_json('MOCK_DATA.json')


def import_data(file_path):
    # what if a field is missing ?
    # what if we try to insert a duplicate ?
    df = pd.read_json(file_path)
    for employee in df[:2]:
        industry = Industry.objects.get_or_create(
            name=employee.industry
        )
        Employee.objects.create(
            first_name=employee.first_name,
            last_name=employee.last_name,
            email=employee.email,
            gender=employee.gender,
            date_of_birth=employee.date_of_birth,
            industry=industry,
            salary=employee.salary,
            years_of_experience=employee.years_of_experience,
        )
        print(f"Successfully added {employee}")
