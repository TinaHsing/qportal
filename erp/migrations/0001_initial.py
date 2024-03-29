# Generated by Django 3.2.4 on 2022-03-01 07:54

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='addSubProduct',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
            ],
        ),
        migrations.CreateModel(
            name='bomDefine',
            fields=[
                ('bomserial', models.AutoField(primary_key=True, serialize=False)),
                ('discription', models.CharField(blank=True, max_length=100, null=True)),
                ('date', models.DateField(blank=True, null=True)),
            ],
        ),
        migrations.CreateModel(
            name='customer',
            fields=[
                ('cid', models.AutoField(primary_key=True, serialize=False)),
                ('name', models.CharField(max_length=100)),
                ('vax', models.CharField(blank=True, max_length=8, null=True)),
                ('contact', models.CharField(blank=True, max_length=30, null=True)),
                ('email', models.CharField(max_length=50)),
                ('phone', models.CharField(blank=True, max_length=20, null=True)),
                ('mobile', models.CharField(blank=True, max_length=20, null=True)),
                ('fax', models.CharField(blank=True, max_length=20, null=True)),
                ('add', models.CharField(blank=True, max_length=150, null=True)),
                ('other', models.CharField(blank=True, max_length=50, null=True)),
            ],
        ),
        migrations.CreateModel(
            name='partNumber',
            fields=[
                ('Pid', models.AutoField(primary_key=True, serialize=False)),
                ('name', models.CharField(help_text='check partNumber rule for detail', max_length=80, unique=True)),
                ('location', models.CharField(blank=True, max_length=15, null=True)),
                ('level', models.PositiveIntegerField(default=0)),
                ('discription', models.TextField(blank=True, help_text='must input key paramter discription here', null=True)),
                ('buylink', models.CharField(blank=True, help_text='input the purchasing link', max_length=200)),
                ('date', models.DateField(blank=True, null=True)),
                ('approve', models.BooleanField(default=False)),
            ],
        ),
        migrations.CreateModel(
            name='QtyReason',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('reason', models.CharField(choices=[('purchasing', 'purchasing'), ('production', 'production'), ('testing', 'testing'), ('sold', 'sold'), ('discard', 'discard'), ('matchQty', 'matchQty'), ('experiment', 'experiment')], default='purchasing', max_length=10)),
            ],
        ),
        migrations.CreateModel(
            name='software',
            fields=[
                ('Sid', models.AutoField(primary_key=True, serialize=False)),
                ('name', models.CharField(max_length=30)),
                ('pc', models.BooleanField(default=False)),
                ('discription', models.CharField(max_length=100)),
                ('history', models.TextField(blank=True, help_text='reversion history', null=True)),
            ],
        ),
        migrations.CreateModel(
            name='testlink',
            fields=[
                ('pn', models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, primary_key=True, serialize=False, to='erp.partnumber')),
                ('testurl', models.CharField(max_length=200)),
            ],
        ),
        migrations.CreateModel(
            name='purchaseList',
            fields=[
                ('plserial', models.AutoField(primary_key=True, serialize=False)),
                ('Qty', models.IntegerField(default=0)),
                ('reqDate', models.DateField(blank=True, null=True)),
                ('status', models.BooleanField(default=True)),
                ('closeDate', models.DateField(blank=True, null=True)),
                ('partNumber', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to='erp.partnumber')),
                ('user', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='user', to=settings.AUTH_USER_MODEL)),
            ],
        ),
        migrations.CreateModel(
            name='pnQty',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('Qty', models.IntegerField(default=0)),
                ('date', models.DateField(blank=True, null=True)),
                ('untestQty', models.IntegerField(default=0)),
                ('partNumber', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to='erp.partnumber')),
                ('reason', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to='erp.qtyreason')),
                ('user', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, to=settings.AUTH_USER_MODEL)),
            ],
        ),
        migrations.CreateModel(
            name='pnCategory',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('category', models.CharField(max_length=10)),
                ('date', models.DateField(blank=True, null=True)),
                ('user', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, to=settings.AUTH_USER_MODEL)),
            ],
        ),
        migrations.CreateModel(
            name='planerElement',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('produceQty', models.IntegerField(default=1)),
                ('bf', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to='erp.bomdefine')),
                ('user', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, to=settings.AUTH_USER_MODEL)),
            ],
        ),
        migrations.AddField(
            model_name='partnumber',
            name='category',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, to='erp.pncategory'),
        ),
        migrations.AddField(
            model_name='partnumber',
            name='software',
            field=models.ManyToManyField(blank=True, to='erp.software'),
        ),
        migrations.AddField(
            model_name='partnumber',
            name='user',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, to=settings.AUTH_USER_MODEL),
        ),
        migrations.CreateModel(
            name='partNote',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('value', models.CharField(blank=True, max_length=15, null=True)),
                ('package', models.CharField(blank=True, max_length=15, null=True)),
                ('param2', models.CharField(blank=True, max_length=15, null=True)),
                ('addBuylink', models.CharField(blank=True, max_length=100, null=True)),
                ('param1', models.CharField(blank=True, max_length=15, null=True)),
                ('part', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to='erp.partnumber')),
            ],
        ),
        migrations.CreateModel(
            name='mpList',
            fields=[
                ('mpSerial', models.AutoField(primary_key=True, serialize=False)),
                ('Qty', models.IntegerField(default=0)),
                ('reqDate', models.DateField()),
                ('status', models.BooleanField(default=True)),
                ('closeDate', models.DateField(blank=True, null=True)),
                ('customer', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to='erp.customer')),
                ('partNumber', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to='erp.partnumber')),
            ],
        ),
        migrations.CreateModel(
            name='endProduct',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('serial', models.IntegerField(blank=True, null=True)),
                ('mDate', models.DateField(blank=True, null=True)),
                ('tDate', models.DateField(blank=True, null=True)),
                ('sDate', models.DateField(blank=True, null=True)),
                ('status', models.CharField(default='untested', max_length=10)),
                ('note', models.TextField(blank=True, help_text='Note', null=True)),
                ('bom', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to='erp.bomdefine')),
                ('customer', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, to='erp.customer')),
                ('mUser', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
                ('part', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to='erp.partnumber')),
                ('sUser', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='sales', to=settings.AUTH_USER_MODEL)),
                ('software', models.ManyToManyField(blank=True, to='erp.software')),
                ('subProduct', models.ManyToManyField(related_name='subp', through='erp.addSubProduct', to='erp.endProduct')),
                ('tUser', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='tester', to=settings.AUTH_USER_MODEL)),
            ],
        ),
        migrations.CreateModel(
            name='elePrice',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('price', models.DecimalField(decimal_places=2, max_digits=10)),
                ('date', models.DateField(blank=True, null=True)),
                ('partNumber', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to='erp.partnumber')),
                ('user', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, to=settings.AUTH_USER_MODEL)),
            ],
        ),
        migrations.CreateModel(
            name='ccnList',
            fields=[
                ('ccnSerial', models.AutoField(primary_key=True, serialize=False)),
                ('reqDate', models.DateField()),
                ('status', models.BooleanField(default=True)),
                ('failure', models.TextField(blank=True, help_text='input failure phenomenon', null=True)),
                ('rootCause', models.TextField(blank=True, help_text='input the rootCause of failure', null=True)),
                ('closeDate', models.DateField(blank=True, null=True)),
                ('closeEng', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, to=settings.AUTH_USER_MODEL)),
                ('endp', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, to='erp.endproduct')),
                ('software', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, to='erp.software')),
            ],
        ),
        migrations.CreateModel(
            name='BomElement',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('unitQty', models.IntegerField(default=1)),
                ('schPN', models.CharField(blank=True, max_length=1000, null=True)),
                ('date', models.DateField(blank=True, null=True)),
                ('bf', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to='erp.bomdefine')),
                ('part', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='element', to='erp.partnumber')),
                ('user', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, to=settings.AUTH_USER_MODEL)),
            ],
        ),
        migrations.AddField(
            model_name='bomdefine',
            name='product',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to='erp.partnumber'),
        ),
        migrations.AddField(
            model_name='bomdefine',
            name='user',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, to=settings.AUTH_USER_MODEL),
        ),
        migrations.AddField(
            model_name='addsubproduct',
            name='child',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='child', to='erp.endproduct'),
        ),
        migrations.AddField(
            model_name='addsubproduct',
            name='mother',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='mother', to='erp.endproduct'),
        ),
    ]
