# Generated by Django 4.1.4 on 2023-01-27 13:10

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('store', '0034_marketplace_is_active'),
    ]

    operations = [
        migrations.AddField(
            model_name='marketplace',
            name='tid',
            field=models.IntegerField(blank=True, null=True),
        ),
    ]