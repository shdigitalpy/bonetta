# Generated by Django 4.1.4 on 2024-11-29 19:42

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('store', '0042_rename_elemente_elemente_artikel'),
    ]

    operations = [
        migrations.CreateModel(
            name='Elemente_Bestellungen',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('kunden_nr', models.CharField(blank=True, max_length=255, null=True)),
                ('betrieb_person', models.CharField(blank=True, max_length=255, null=True)),
                ('adresse', models.CharField(blank=True, max_length=255, null=True)),
                ('plz', models.CharField(blank=True, max_length=255, null=True)),
                ('elemente_nr', models.CharField(blank=True, max_length=255, null=True)),
                ('montage', models.CharField(blank=True, max_length=255, null=True)),
                ('bemerkung', models.CharField(blank=True, max_length=255, null=True)),
            ],
            options={
                'ordering': ['id'],
            },
        ),
    ]
