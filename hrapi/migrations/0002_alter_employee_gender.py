# Generated by Django 4.2 on 2023-04-27 17:59

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('hrapi', '0001_initial'),
    ]

    operations = [
        migrations.AlterField(
            model_name='employee',
            name='gender',
            field=models.CharField(choices=[('M', 'Male'), ('F', 'Female')], max_length=1, null=True),
        ),
    ]
