# Generated by Django 3.2.13 on 2022-07-12 01:26

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('users', '0005_alter_user_image_date_created'),
    ]

    operations = [
        migrations.AddField(
            model_name='user',
            name='primary_image',
            field=models.UUIDField(blank=True, null=True),
        ),
    ]