# Generated by Django 4.1.4 on 2025-02-18 07:00

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('store', '0073_elemente_bestellungen_artikel'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='elemente_bestellungen',
            name='artikel',
        ),
        migrations.AddField(
            model_name='elementecartitem',
            name='artikel',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='elementebestellung_artikel', to='store.artikel'),
        ),
    ]
