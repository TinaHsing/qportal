# Generated by Django 3.0.3 on 2020-09-22 04:35

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('erp', '0020_auto_20200922_0252'),
    ]

    operations = [
        migrations.AddField(
            model_name='pnqty',
            name='discardQty',
            field=models.IntegerField(default=0),
        ),
    ]
