# Generated by Django 4.1.4 on 2025-06-02 09:18

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('store', '0015_alter_item_options_and_more'),
    ]

    operations = [
        migrations.AddField(
            model_name='marke',
            name='bestseller',
            field=models.BooleanField(default=False),
        ),
    ]
