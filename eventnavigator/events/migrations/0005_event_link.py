# Generated by Django 2.2.7 on 2019-12-05 20:44

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('events', '0004_auto_20191204_2258'),
    ]

    operations = [
        migrations.AddField(
            model_name='event',
            name='link',
            field=models.CharField(blank=True, max_length=200),
        ),
    ]
