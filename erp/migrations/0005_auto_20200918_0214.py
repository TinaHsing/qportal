# Generated by Django 3.0.3 on 2020-09-18 02:14

import datetime
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('erp', '0004_auto_20200917_1706'),
    ]

    operations = [
        migrations.CreateModel(
            name='pnCategory',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('category', models.CharField(max_length=10)),
            ],
        ),
        migrations.AlterField(
            model_name='partnumber',
            name='date',
            field=models.DateField(default=datetime.date(2020, 9, 18)),
        ),
        migrations.AlterField(
            model_name='partnumber',
            name='category',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='erp.pnCategory'),
        ),
    ]
