# Generated by Django 4.1.4 on 2025-04-22 05:52

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('store', '0011_alter_elemente_bestellungen_wer'),
    ]

    operations = [
        migrations.AlterField(
            model_name='elementecartitem',
            name='element_nr',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='elemente_cart_items', to='store.elemente'),
        ),
    ]
