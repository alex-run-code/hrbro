from django.db import models


# Create your models here.
class Industry(models.Model):
    name = models.CharField(max_length=100, unique=True)


class Employee(models.Model):
    GENDER_CHOICES = (
        ('M', 'Male'),
        ('F', 'Female'),
    )

    first_name = models.CharField(max_length=100)
    last_name = models.CharField(max_length=100)
    # we could decide to not have it unique, but it wouldn't make sense
    email = models.EmailField(max_length=254, unique=True)
    gender = models.CharField(max_length=1, choices=GENDER_CHOICES, null=True)
    date_of_birth = models.DateField()
    industry = models.ForeignKey(Industry, on_delete=models.CASCADE)
    salary = models.DecimalField(decimal_places=2, max_digits=10)
    years_of_experience = models.IntegerField()

    def __str__(self):
        return f"{self.first_name} {self.last_name}"

    # first and last name could be used to make a unique combination like this :
    # but in bigger companies / countries, it's actually possible to have
    # two employees with same name and surname, so we won't do it
    #
    # class Meta:
    #     unique_together = ('first_name', 'first_name')
