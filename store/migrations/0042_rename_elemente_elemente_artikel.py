# Generated by Django 4.1.4 on 2024-11-29 16:41

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('store', '0041_remove_artikel_elemente_elemente_elemente'),
    ]

    operations = [
        migrations.RenameField(
            model_name='elemente',
            old_name='elemente',
            new_name='artikel',
        ),
    ]