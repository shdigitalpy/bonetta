# Generated by Django 4.1.4 on 2023-01-19 12:53

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('store', '0028_alter_elemente_options_kunde_interne_nummer'),
    ]

    operations = [
        migrations.CreateModel(
            name='Marke',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=255)),
                ('slug', models.SlugField(max_length=255)),
            ],
            options={
                'verbose_name': 'Marke',
                'verbose_name_plural': 'Marken',
                'ordering': ['id'],
            },
        ),
        migrations.AddField(
            model_name='item',
            name='marke',
            field=models.ForeignKey(blank=True, default=None, null=True, on_delete=django.db.models.deletion.SET_NULL, to='store.marke'),
        ),
    ]