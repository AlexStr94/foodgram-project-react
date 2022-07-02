import csv
from pathlib import Path

from django.db import migrations, transaction


data_path = Path(__file__).resolve().parents[2] / 'ingredients.csv'
try:
    with open(data_path, encoding='utf-8') as f:
        data = [list(line) for line in csv.reader(f)]
except Exception:
    data = []


def add_ingredients(apps, schema_editor):
    MeasurementUnit = apps.get_model('recipes', 'MeasurementUnit')
    Ingredient = apps.get_model('recipes', 'Ingredient')
    for ingredient in data:
        with transaction.atomic():
            try:
                measurement_unit = MeasurementUnit.objects.get(
                    name=ingredient[1]
                )
                Ingredient.objects.create(
                    name=ingredient[0],
                    measurement_unit=measurement_unit
                )
            except:
                continue


def remove_ingredients(apps, schema_editor):
    Ingredient = apps.get_model('recipes', 'Ingredient')
    for ingredient in data:
        try:
            Ingredient.objects.get(
                name=ingredient[0]
            ).delete()
        except Exception:
            continue


class Migration(migrations.Migration):

    dependencies = [
        ('recipes', '0004_add_measurement_unit'),
    ]

    operations = [
        migrations.RunPython(
            add_ingredients,
            remove_ingredients
        )
    ]
