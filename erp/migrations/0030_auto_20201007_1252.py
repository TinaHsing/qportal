# Generated by Django 3.0.3 on 2020-10-07 12:52

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('erp', '0029_bomdefine'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='bomelement',
            name='bomserial',
        ),
        migrations.RemoveField(
            model_name='bomelement',
            name='product',
        ),
        migrations.AddField(
            model_name='bomelement',
            name='bf',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to='erp.bomDefine'),
        ),
    ]
