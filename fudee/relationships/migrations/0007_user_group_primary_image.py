# Generated by Django 3.2.13 on 2022-07-11 02:30

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('relationships', '0006_remove_user_group_image'),
    ]

    operations = [
        migrations.AddField(
            model_name='user_group',
            name='primary_image',
            field=models.UUIDField(blank=True, null=True),
        ),
    ]
