# Generated by Django 3.2.13 on 2022-07-13 08:29

from django.db import migrations
import recurrence.fields


class Migration(migrations.Migration):

    dependencies = [
        ('events', '0004_auto_20220713_0004'),
    ]

    operations = [
        migrations.AlterField(
            model_name='event',
            name='recurrences',
            field=recurrence.fields.RecurrenceField(blank=True),
        ),
    ]