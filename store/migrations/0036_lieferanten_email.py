# Generated by Django 4.1.4 on 2024-11-29 14:21

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('store', '0035_elemente_lieferant'),
    ]

    operations = [
        migrations.AddField(
            model_name='lieferanten',
            name='email',
            field=models.CharField(blank=True, max_length=255, null=True),
        ),
    ]