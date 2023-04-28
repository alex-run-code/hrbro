from rest_framework.viewsets import ModelViewSet
from rest_framework.response import Response
from rest_framework.views import APIView
from hrapi.models import Employee, Industry
from hrapi.serializers import EmployeeSerializer, IndustrySerializer
import pandas as pd
from datetime import datetime

# ModelViewSet is super strong. But sometimes it's not what we want
# for example :
#
# Custom functionality: Sometimes we need to implement custom
# functionality that is not provided by ModelViewSet. For example,
# if we want to implement a search functionality for a specific field
# in the model, we may need to use a custom view that provides this
# functionality.
#
# Performance: ModelViewSet can be slower than other views in
# some cases, especially when dealing with large datasets or
# complex queries. In such cases, we may need to use other
# views that provide better performance.
#
# Security: ModelViewSet assumes that all CRUD operations
# are allowed for all users. If we need to implement more
# fine-grained permissions or authentication, we may need
# to use other views that provide this functionality.
#
# Flexibility: ModelViewSet is a generic view that provides
# a standard set of functionality for CRUD operations. If
# we need to implement more complex or specific functionality,
# we may need to use other views that provide more flexibility
# and customization options.


class EmployeeViewSet(ModelViewSet):
    queryset = Employee.objects.all()
    serializer_class = EmployeeSerializer


class IndustryViewSet(ModelViewSet):
    queryset = Industry.objects.all()
    serializer_class = IndustrySerializer


def get_age(date_of_birth):
    now = datetime.now()
    age = now.year - date_of_birth.year - ((now.month, now.day) < (date_of_birth.month, date_of_birth.day))
    return age


def prettify_brackets(bracket_str):
    pretty_bracket = bracket_str.replace('(', '').replace(']', '').replace(',', ' to').replace('to inf', '+')
    return pretty_bracket


class GeneralStatistic(APIView):

    def get(self, request):
        employees = Employee.objects.all().select_related('industry')
        df = pd.DataFrame(employees.values(
            'id', 'first_name', 'last_name', 'email', 'gender',
            'date_of_birth', 'salary', 'years_of_experience',
            'industry__name'
        ))

        # adding an age column
        df['age'] = df['date_of_birth'].apply(get_age)

        # more clarity in api output
        df = df.rename(columns={'industry__name': 'industry'})

        # grouping, averaging
        industry_stats = df.groupby('industry').agg(
            {
                'salary': 'mean',
                'years_of_experience': 'mean',
                'age': 'mean'
            }
        )

        # rounding happen after calculation for more accuracy
        industry_stats['salary'] = industry_stats['salary'].astype(float).round(2)
        industry_stats['years_of_experience'] = industry_stats['years_of_experience'].round(2)
        industry_stats['age'] = industry_stats['age'].round(1)

        industry_stats = industry_stats.reset_index()
        industry_stats = industry_stats.sort_values('salary', ascending=False)

        # Convert the pandas dataframe to a JSON response
        response_data = industry_stats.to_dict(orient='records')
        return Response(response_data)


class YoEStats(APIView):

    def get(self, request):
        employees = Employee.objects.all()
        df = pd.DataFrame(employees.values())
        # Define the bins for the years of experience
        bins = [0, 5, 10, 15, 20, 25, 30, float('inf')]

        # Bin edges are exclusive on the right side.
        # So someone with exactly 5 years of experience would fall into the 5-10
        labels = ['1-5', '5-10', '10-15', '15-20', '20-25', '25-30', 'More than 30']
        df['experience_bracket'] = pd.cut(
            df['years_of_experience'], bins=bins, labels=labels)

        # Group by the experience bracket and calculate the mean salary
        salary_by_experience = df.groupby('experience_bracket')['salary'].mean()
        salary_by_experience = salary_by_experience.astype(float).round(2)
        salary_by_experience = salary_by_experience.reset_index()

        # Convert the pandas dataframe to a JSON response
        response_data = salary_by_experience.to_dict(orient='records')
        return Response(response_data)


class Agism(APIView):

    def get(self, request):
        employees = Employee.objects.all()
        df = pd.DataFrame(employees.values())

        # adding an age column
        df['age'] = df['date_of_birth'].apply(get_age)

        # define age bins and labels
        age_bins = [20, 30, 40, 50, float('inf')]
        year_bins = [0, 5, 10, 15, 20, 30, float('inf')]

        result = df.groupby([pd.cut(
            df['years_of_experience'], year_bins), pd.cut(df['age'], age_bins)])[
            'salary'].mean()

        # create a nested dictionary of results
        response_data = {}
        for years, age in result.index:
            years_str = prettify_brackets(str(years)) + ' years of experience'
            age_str = prettify_brackets(str(age)) + ' years old'
            salary = result[(years, age)]
            if years_str not in response_data:
                response_data[years_str] = {}
            response_data[years_str][age_str] = round(float(salary), 2)

        # Return the response
        return Response(response_data)


class Sexism(APIView):

    def get(self, request):

        employees = Employee.objects.all()
        df = pd.DataFrame(employees.values())

        year_bins = [0, 5, 10, 15, 20, 30, float('inf')]

        # Drop gender column before grouping by gender and years_of_experience bins
        result = df.drop('gender', axis=1)\
            .groupby([df['gender'], pd.cut(df['years_of_experience'], year_bins)])[
            'salary'].mean()
        result = result.reset_index()

        result['years_of_experience'] = result['years_of_experience'].astype(str)\
            .str.replace('(', '').str.replace(']', '').str.replace(',', ' to')

        # Group by gender again to create separate sections for males and females
        result = result.groupby('gender')\
            .apply(lambda x: x.drop('gender', axis=1)
                   .to_dict(orient='records')).to_dict()

        return Response(result)


# Average age per industry - done
# Average salaries per industry - done
# Average salaries per years of experience - done
# Based on the dataset, other “interesting” statistics


# Do old people with same amount of YoE earn less money ?
# Get people aged 20-30 (Young)
# Get people aged 30-40 (Old)
# Get average Young earning per YoE
# Get average Old earning per YoE


# Do women with same amount of YoE earn less money ?
# What industry is the most profitable ?
# What industry offer the fastest career growth ?
# What industry attract younger people ?
# What industry attract more women ?

