# Generated by Django 4.1.4 on 2024-09-13 19:06

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('store', '0025_alter_crmaddress_crm_kanton'),
    ]

    operations = [
        migrations.AlterField(
            model_name='kunde',
            name='last_service',
            field=models.DateTimeField(blank=True, null=True),
        ),
    ]
