# Generated by Django 4.1.3 on 2023-03-06 08:11

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('pst', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='user',
            name='categories_created',
            field=models.BooleanField(default=False),
        ),
    ]
