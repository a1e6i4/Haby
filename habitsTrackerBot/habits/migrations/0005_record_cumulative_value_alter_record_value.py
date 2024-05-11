# Generated by Django 4.2.6 on 2023-12-30 03:41

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('habits', '0004_goal_created_at'),
    ]

    operations = [
        migrations.AddField(
            model_name='record',
            name='cumulative_value',
            field=models.FloatField(default=0),
        ),
        migrations.AlterField(
            model_name='record',
            name='value',
            field=models.FloatField(default=0),
        ),
    ]