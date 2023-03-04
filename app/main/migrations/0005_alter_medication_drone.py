# Generated by Django 4.1.7 on 2023-03-03 17:05

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('main', '0004_alter_medication_image'),
    ]

    operations = [
        migrations.AlterField(
            model_name='medication',
            name='drone',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='medications', to='main.drone'),
        ),
    ]