# Generated by Django 4.1.4 on 2024-12-11 08:20

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('store', '0054_remove_artikel_vp'),
    ]

    operations = [
        migrations.AddField(
            model_name='artikel',
            name='lagerort',
            field=models.CharField(blank=True, max_length=255, null=True),
        ),
    ]