# Generated by Django 4.1.3 on 2023-02-07 00:16

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('pst', '0002_remove_spending_file_categories'),
    ]

    operations = [
        migrations.AddField(
            model_name='categories',
            name='categories_type',
            field=models.CharField(choices=[('Expenditure', 'Expenditure'), ('Income', 'Income')], default='Expenditure', max_length=30),
        ),
    ]
