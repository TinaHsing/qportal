# Generated by Django 3.1.4 on 2020-12-15 04:34

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('erp', '0004_ccnlist_customer_mplist'),
    ]

    operations = [
        migrations.AddField(
            model_name='ccnlist',
            name='failure',
            field=models.TextField(blank=True, null=True, verbose_name=models.TextField(help_text='input failure phenomenon')),
        ),
    ]
