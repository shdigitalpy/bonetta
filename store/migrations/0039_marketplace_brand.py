# Generated by Django 4.1.4 on 2023-02-06 09:43

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('store', '0038_remove_item_marke_marke_item'),
    ]

    operations = [
        migrations.AddField(
            model_name='marketplace',
            name='brand',
            field=models.CharField(blank=True, max_length=255, null=True),
        ),
    ]