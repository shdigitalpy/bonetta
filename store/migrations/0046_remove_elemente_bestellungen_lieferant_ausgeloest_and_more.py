# Generated by Django 4.1.4 on 2024-11-29 20:34

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('store', '0045_elemente_bestellungen_lieferant_ausgeloest_and_more'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='elemente_bestellungen',
            name='lieferant_ausgeloest',
        ),
        migrations.RemoveField(
            model_name='elemente_bestellungen',
            name='lieferant_date',
        ),
        migrations.AddField(
            model_name='elemente_bestellungen',
            name='lieferschein_pdf',
            field=models.FileField(blank=True, null=True, upload_to='lieferscheine/'),
        ),
    ]
