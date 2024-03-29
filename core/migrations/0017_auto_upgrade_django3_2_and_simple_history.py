# Generated by Django 3.2.23 on 2023-11-29 04:39

import core.utils
import django.contrib.gis.db.models.fields
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0016_add_resolved'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='historicalhelprequest',
            options={'get_latest_by': ('history_date', 'history_id'), 'ordering': ('-history_date', '-history_id'), 'verbose_name': 'historical help request', 'verbose_name_plural': 'historical help requests'},
        ),
        migrations.AlterModelOptions(
            name='historicaluser',
            options={'get_latest_by': ('history_date', 'history_id'), 'ordering': ('-history_date', '-history_id'), 'verbose_name': 'historical user', 'verbose_name_plural': 'historical users'},
        ),
        migrations.AlterField(
            model_name='helprequest',
            name='added',
            field=models.DateTimeField(auto_now_add=True, db_index=True, null=True, verbose_name='Added'),
        ),
        migrations.AlterField(
            model_name='helprequest',
            name='address',
            field=models.CharField(help_text='Your address, city, neighborhood, references, or how to get there, to get help', max_length=400, null=True, verbose_name='Address'),
        ),
        migrations.AlterField(
            model_name='helprequest',
            name='location',
            field=django.contrib.gis.db.models.fields.PointField(help_text='<p style="margin-bottom:5px;font-size:10px;">Select your location so that people can find you, if you do not want to mark your home a good option may be the nearest police station or some other nearby public place.<br>If you have problems with this step <a href="#" class="is-link modal-button" data-target="#myModal" aria-haspopup="true">Check out this help</a></p><p id="div_direccion" style="font-size: 10px; margin-bottom: 5px;"></p>', srid=4326, verbose_name='Location'),
        ),
        migrations.AlterField(
            model_name='helprequest',
            name='message',
            field=models.TextField(db_index=True, help_text='Here you can tell in detail what you need, <b> the better you tell your situation the more likely they want to help you </b>', max_length=2000, null=True, verbose_name='Request Description'),
        ),
        migrations.AlterField(
            model_name='helprequest',
            name='name',
            field=models.CharField(max_length=200, verbose_name='Name and surname'),
        ),
        migrations.AlterField(
            model_name='helprequest',
            name='phone',
            field=models.CharField(max_length=30, verbose_name='Telephone contact'),
        ),
        migrations.AlterField(
            model_name='helprequest',
            name='picture',
            field=models.ImageField(blank=True, help_text='In case you want you can attach a photo related to your request. It is optional but it can help people better understand your situation.', null=True, upload_to=core.utils.rename_img, verbose_name='Photo'),
        ),
        migrations.AlterField(
            model_name='helprequest',
            name='title',
            field=models.CharField(db_index=True, help_text='Short description of what you need', max_length=200, verbose_name='Request title'),
        ),
        migrations.AlterField(
            model_name='historicalhelprequest',
            name='added',
            field=models.DateTimeField(blank=True, db_index=True, editable=False, null=True, verbose_name='Added'),
        ),
        migrations.AlterField(
            model_name='historicalhelprequest',
            name='address',
            field=models.CharField(help_text='Your address, city, neighborhood, references, or how to get there, to get help', max_length=400, null=True, verbose_name='Address'),
        ),
        migrations.AlterField(
            model_name='historicalhelprequest',
            name='history_date',
            field=models.DateTimeField(db_index=True),
        ),
        migrations.AlterField(
            model_name='historicalhelprequest',
            name='location',
            field=django.contrib.gis.db.models.fields.PointField(help_text='<p style="margin-bottom:5px;font-size:10px;">Select your location so that people can find you, if you do not want to mark your home a good option may be the nearest police station or some other nearby public place.<br>If you have problems with this step <a href="#" class="is-link modal-button" data-target="#myModal" aria-haspopup="true">Check out this help</a></p><p id="div_direccion" style="font-size: 10px; margin-bottom: 5px;"></p>', srid=4326, verbose_name='Location'),
        ),
        migrations.AlterField(
            model_name='historicalhelprequest',
            name='message',
            field=models.TextField(db_index=True, help_text='Here you can tell in detail what you need, <b> the better you tell your situation the more likely they want to help you </b>', max_length=2000, null=True, verbose_name='Request Description'),
        ),
        migrations.AlterField(
            model_name='historicalhelprequest',
            name='name',
            field=models.CharField(max_length=200, verbose_name='Name and surname'),
        ),
        migrations.AlterField(
            model_name='historicalhelprequest',
            name='phone',
            field=models.CharField(max_length=30, verbose_name='Telephone contact'),
        ),
        migrations.AlterField(
            model_name='historicalhelprequest',
            name='picture',
            field=models.TextField(blank=True, help_text='In case you want you can attach a photo related to your request. It is optional but it can help people better understand your situation.', max_length=100, null=True, verbose_name='Photo'),
        ),
        migrations.AlterField(
            model_name='historicalhelprequest',
            name='title',
            field=models.CharField(db_index=True, help_text='Short description of what you need', max_length=200, verbose_name='Request title'),
        ),
        migrations.AlterField(
            model_name='historicaluser',
            name='history_date',
            field=models.DateTimeField(db_index=True),
        ),
    ]
