# Generated by Django 2.2.7 on 2019-12-04 22:46

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('events', '0002_event_end_date'),
    ]

    operations = [
        migrations.AddField(
            model_name='event',
            name='image',
            field=models.ImageField(blank=True, upload_to='event_image'),
        ),
    ]
