# Generated by Django 4.1.4 on 2024-10-18 18:21

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('store', '0033_lieferanten_alter_elemente_nettopreis_and_more'),
    ]

    operations = [
        migrations.AddField(
            model_name='objekte',
            name='lieferant',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='objekte_lieferanten', to='store.lieferanten'),
        ),
    ]
