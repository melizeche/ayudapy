# Generated by Django 2.2.11 on 2020-10-06 03:37

from django.conf import settings
import django.contrib.gis.db.models.fields
from django.db import migrations, models
import django.db.models.deletion
import simple_history.models


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('org', '0002_historicaldonationcenter'),
    ]

    operations = [
        migrations.CreateModel(
            name='Pool',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('location', django.contrib.gis.db.models.fields.PointField(srid=4326, verbose_name='Ubicación')),
                ('address', models.CharField(help_text='Dirección, ciudad, barrio, referencias, o cómo llegar', max_length=400, null=True, verbose_name='Dirección')),
                ('city', models.CharField(blank=True, default='', editable=False, max_length=30)),
                ('city_code', models.CharField(blank=True, default='', editable=False, max_length=30)),
                ('active', models.BooleanField(db_index=True, default=True)),
                ('added', models.DateTimeField(auto_now_add=True, db_index=True, null=True, verbose_name='Agregado')),
                ('name', models.CharField(help_text='Nombre de la persona encargada', max_length=200, verbose_name='Nombre y Apellido')),
                ('phone', models.CharField(max_length=30, verbose_name='Teléfono de contacto')),
                ('info', models.TextField(blank=True, help_text='Cantidad de litros o dimensiones, ¿es una piscina o un reservorio?, etc...', null=True, verbose_name='Información')),
            ],
            options={
                'abstract': False,
            },
        ),
        migrations.CreateModel(
            name='HistoricalPool',
            fields=[
                ('id', models.IntegerField(auto_created=True, blank=True, db_index=True, verbose_name='ID')),
                ('location', django.contrib.gis.db.models.fields.PointField(srid=4326, verbose_name='Ubicación')),
                ('address', models.CharField(help_text='Dirección, ciudad, barrio, referencias, o cómo llegar', max_length=400, null=True, verbose_name='Dirección')),
                ('city', models.CharField(blank=True, default='', editable=False, max_length=30)),
                ('city_code', models.CharField(blank=True, default='', editable=False, max_length=30)),
                ('active', models.BooleanField(db_index=True, default=True)),
                ('added', models.DateTimeField(blank=True, db_index=True, editable=False, null=True, verbose_name='Agregado')),
                ('name', models.CharField(help_text='Nombre de la persona encargada', max_length=200, verbose_name='Nombre y Apellido')),
                ('phone', models.CharField(max_length=30, verbose_name='Teléfono de contacto')),
                ('info', models.TextField(blank=True, help_text='Cantidad de litros o dimensiones, ¿es una piscina o un reservorio?, etc...', null=True, verbose_name='Información')),
                ('history_id', models.AutoField(primary_key=True, serialize=False)),
                ('history_date', models.DateTimeField()),
                ('history_change_reason', models.CharField(max_length=100, null=True)),
                ('history_type', models.CharField(choices=[('+', 'Created'), ('~', 'Changed'), ('-', 'Deleted')], max_length=1)),
                ('history_user', models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='+', to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'verbose_name': 'historical pool',
                'ordering': ('-history_date', '-history_id'),
                'get_latest_by': 'history_date',
            },
            bases=(simple_history.models.HistoricalChanges, models.Model),
        ),
    ]