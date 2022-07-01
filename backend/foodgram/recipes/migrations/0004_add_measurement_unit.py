import csv
from pathlib import Path

from django.db import migrations

data_path = Path(__file__).resolve().parents[2] / 'ingredients.csv'
try:
    with open(data_path, encoding='utf-8') as f:
        data = [list(line) for line in csv.reader(f)]
except Exception:
    data = []


def add_measurement_unit(apps, schema_editor):
    MeasurementUnit = apps.get_model('recipes', 'MeasurementUnit')
    for ingredient in data:
        try:
            MeasurementUnit.objects.get_or_create(
                name=ingredient[1]
            )
        except Exception:
            continue


def remove_measurement_unit(apps, schema_editor):
    MeasurementUnit = apps.get_model('recipes', 'MeasurementUnit')
    for ingredient in data:
        try:
            MeasurementUnit.objects.get(
                name=ingredient[1]
            ).delete()
        except Exception:
            continue


class Migration(migrations.Migration):

    dependencies = [
        ('recipes', '0003_alter_recipe_options'),
    ]

    operations = [
        migrations.RunPython(
            add_measurement_unit,
            remove_measurement_unit
        )
    ]
