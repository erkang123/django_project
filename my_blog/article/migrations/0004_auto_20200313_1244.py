# Generated by Django 2.1.5 on 2020-03-13 04:44

from django.db import migrations, models
import django.utils.timezone


class Migration(migrations.Migration):

    dependencies = [
        ('article', '0003_auto_20200310_2120'),
    ]

    operations = [
        migrations.AlterField(
            model_name='articlepost',
            name='created',
            field=models.DateTimeField(default=django.utils.timezone.now),
        ),
    ]