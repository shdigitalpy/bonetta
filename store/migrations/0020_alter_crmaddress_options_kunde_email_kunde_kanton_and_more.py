# Generated by Django 4.1.4 on 2024-09-13 17:58

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('store', '0019_alter_objekte_objekte_crmaddress'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='crmaddress',
            options={'verbose_name': 'CRM-Adresse', 'verbose_name_plural': 'CRM-Adressen'},
        ),
        migrations.AddField(
            model_name='kunde',
            name='email',
            field=models.CharField(blank=True, max_length=255, null=True),
        ),
        migrations.AddField(
            model_name='kunde',
            name='kanton',
            field=models.CharField(blank=True, max_length=255, null=True),
        ),
        migrations.AddField(
            model_name='kunde',
            name='nachname',
            field=models.CharField(blank=True, max_length=255, null=True),
        ),
        migrations.AddField(
            model_name='kunde',
            name='vorname',
            field=models.CharField(blank=True, max_length=255, null=True),
        ),
    ]
