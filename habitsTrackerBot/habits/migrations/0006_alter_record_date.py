# Generated by Django 4.2.6 on 2023-12-30 03:42

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('habits', '0005_record_cumulative_value_alter_record_value'),
    ]

    operations = [
        migrations.AlterField(
            model_name='record',
            name='date',
            field=models.DateField(auto_now_add=True),
        ),
    ]
