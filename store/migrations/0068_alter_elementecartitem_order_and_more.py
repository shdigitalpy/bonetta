# Generated by Django 4.1.4 on 2025-02-06 14:23

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('store', '0067_elemente_bestellungen_status'),
    ]

    operations = [
        migrations.AlterField(
            model_name='elementecartitem',
            name='order',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='elementeitems_bestellung', to='store.elemente_bestellungen'),
        ),
        migrations.DeleteModel(
            name='ElementeCartOrder',
        ),
    ]
