# Generated by Django 4.1.7 on 2023-03-02 17:50

import django.core.validators
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('main', '0001_initial'),
    ]

    operations = [
        migrations.AlterField(
            model_name='drone',
            name='weight_limit',
            field=models.FloatField(help_text='Maximum value 500 grams', validators=[django.core.validators.MinValueValidator(0), django.core.validators.MaxValueValidator(500)], verbose_name='Weight limit (grams)'),
        ),
        migrations.AlterField(
            model_name='medication',
            name='code',
            field=models.TextField(help_text='Only uppercase alphanumeric characters and underscores', validators=[django.core.validators.RegexValidator('^[A-Z0-9\\_]*$')]),
        ),
        migrations.AlterField(
            model_name='medication',
            name='name',
            field=models.TextField(help_text='Only alphanumeric characters, dashes and underscores', validators=[django.core.validators.RegexValidator('^[a-zA-Z0-9\\-\\_]*$')]),
        ),
    ]
