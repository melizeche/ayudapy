# Generated by Django 2.2.12 on 2020-04-24 23:03

import core.utils
from django.conf import settings
import django.contrib.gis.db.models.fields
import django.contrib.postgres.search
from django.db import migrations, models
import django.db.models.deletion
import simple_history.models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='OllaPopular',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('title', models.CharField(db_index=True, help_text='Escribe un nombre para identificar a la Olla Popular', max_length=200, verbose_name='Nombre de la olla popular')),
                ('message', models.TextField(db_index=True, help_text='Acá podés contar detalladamente lo que necesitás para tu olla popular, <b>cuanto mejor cuentes tu situación es más probable que te quieran ayudar</b>', max_length=2000, null=True, verbose_name='Descripción del pedido')),
                ('name', models.CharField(max_length=200, verbose_name='Nombre y Apellido del responsable')),
                ('phone', models.CharField(max_length=30, verbose_name='Teléfono de contacto')),
                ('address', models.CharField(help_text='Para ayudar a quien quiera ayudarte saber la dirección, ciudad, barrio, referencias, o cómo llegar', max_length=400, null=True, verbose_name='Dirección')),
                ('location', django.contrib.gis.db.models.fields.PointField(help_text='<p style="margin-bottom:5px;font-size:10px;">Seleccioná tu ubicación para que la gente pueda encontrarte, si no querés marcar tu casa una buena opción puede ser la comisaría más cercana o algún otro sitio público cercano.            <br>Si tenés problemas con este paso <a href="#" class="is-link modal-button" data-target="#myModal" aria-haspopup="true">mirá esta ayuda</a></p><p id="div_direccion" style="font-size: 10px; margin-bottom: 5px;"></p>', srid=4326, verbose_name='Ubicación')),
                ('picture', models.ImageField(blank=True, help_text='Si querés podés adjuntar una foto relacionada con tu pedido, es opcional pero puede ayudar a que la gente entienda mejor tu situación', null=True, upload_to=core.utils.rename_img, verbose_name='Foto')),
                ('resolved', models.BooleanField(db_index=True, default=False)),
                ('active', models.BooleanField(db_index=True, default=True)),
                ('added', models.DateTimeField(auto_now_add=True, db_index=True, null=True, verbose_name='Agregado')),
                ('upvotes', models.IntegerField(blank=True, default=0)),
                ('downvotes', models.IntegerField(blank=True, default=0)),
                ('city', models.CharField(blank=True, default='', editable=False, max_length=50)),
                ('city_code', models.CharField(blank=True, default='', editable=False, max_length=50)),
                ('search_vector', django.contrib.postgres.search.SearchVectorField()),
            ],
        ),
        migrations.CreateModel(
            name='HistoricalOllaPopular',
            fields=[
                ('id', models.IntegerField(auto_created=True, blank=True, db_index=True, verbose_name='ID')),
                ('title', models.CharField(db_index=True, help_text='Escribe un nombre para identificar a la Olla Popular', max_length=200, verbose_name='Nombre de la olla popular')),
                ('message', models.TextField(db_index=True, help_text='Acá podés contar detalladamente lo que necesitás para tu olla popular, <b>cuanto mejor cuentes tu situación es más probable que te quieran ayudar</b>', max_length=2000, null=True, verbose_name='Descripción del pedido')),
                ('name', models.CharField(max_length=200, verbose_name='Nombre y Apellido del responsable')),
                ('phone', models.CharField(max_length=30, verbose_name='Teléfono de contacto')),
                ('address', models.CharField(help_text='Para ayudar a quien quiera ayudarte saber la dirección, ciudad, barrio, referencias, o cómo llegar', max_length=400, null=True, verbose_name='Dirección')),
                ('location', django.contrib.gis.db.models.fields.PointField(help_text='<p style="margin-bottom:5px;font-size:10px;">Seleccioná tu ubicación para que la gente pueda encontrarte, si no querés marcar tu casa una buena opción puede ser la comisaría más cercana o algún otro sitio público cercano.            <br>Si tenés problemas con este paso <a href="#" class="is-link modal-button" data-target="#myModal" aria-haspopup="true">mirá esta ayuda</a></p><p id="div_direccion" style="font-size: 10px; margin-bottom: 5px;"></p>', srid=4326, verbose_name='Ubicación')),
                ('picture', models.TextField(blank=True, help_text='Si querés podés adjuntar una foto relacionada con tu pedido, es opcional pero puede ayudar a que la gente entienda mejor tu situación', max_length=100, null=True, verbose_name='Foto')),
                ('resolved', models.BooleanField(db_index=True, default=False)),
                ('active', models.BooleanField(db_index=True, default=True)),
                ('added', models.DateTimeField(blank=True, db_index=True, editable=False, null=True, verbose_name='Agregado')),
                ('upvotes', models.IntegerField(blank=True, default=0)),
                ('downvotes', models.IntegerField(blank=True, default=0)),
                ('city', models.CharField(blank=True, default='', editable=False, max_length=50)),
                ('city_code', models.CharField(blank=True, default='', editable=False, max_length=50)),
                ('search_vector', django.contrib.postgres.search.SearchVectorField()),
                ('history_id', models.AutoField(primary_key=True, serialize=False)),
                ('history_date', models.DateTimeField()),
                ('history_change_reason', models.CharField(max_length=100, null=True)),
                ('history_type', models.CharField(choices=[('+', 'Created'), ('~', 'Changed'), ('-', 'Deleted')], max_length=1)),
                ('history_user', models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='+', to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'verbose_name': 'historical olla popular',
                'ordering': ('-history_date', '-history_id'),
                'get_latest_by': 'history_date',
            },
            bases=(simple_history.models.HistoricalChanges, models.Model),
        ),
    ]
