# Generated by Django 4.1.4 on 2024-09-13 18:56

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('store', '0023_remove_marketplace_category_remove_marketplace_user_and_more'),
    ]

    operations = [
        migrations.AlterField(
            model_name='kunde',
            name='last_service',
            field=models.DateField(blank=True, null=True),
        ),
    ]