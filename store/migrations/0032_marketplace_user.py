# Generated by Django 4.1.4 on 2023-01-20 20:40

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('store', '0031_marketplace_mp_category_alter_item_marke'),
    ]

    operations = [
        migrations.AddField(
            model_name='marketplace',
            name='user',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL),
        ),
    ]