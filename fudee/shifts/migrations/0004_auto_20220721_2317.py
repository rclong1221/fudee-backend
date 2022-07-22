# Generated by Django 3.2.13 on 2022-07-22 06:17

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('shifts', '0003_swap'),
    ]

    operations = [
        migrations.AlterField(
            model_name='swap',
            name='old_employee',
            field=models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, related_name='old_employee', to='users.user'),
        ),
        migrations.AlterField(
            model_name='swap',
            name='shift',
            field=models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, related_name='shift', to='shifts.shift'),
        ),
    ]