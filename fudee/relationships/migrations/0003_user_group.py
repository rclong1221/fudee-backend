# Generated by Django 3.2.13 on 2022-06-10 15:35

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion
import uuid


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('relationships', '0002_relationship'),
    ]

    operations = [
        migrations.CreateModel(
            name='User_Group',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('uuid', models.UUIDField(db_index=True, default=uuid.uuid4, editable=False, unique=True)),
                ('name', models.CharField(blank=True, max_length=255, verbose_name='Name of User Group')),
                ('date_created', models.DateField(auto_now_add=True)),
                ('image', models.FileField(blank=True, null=True, upload_to='')),
                ('creator', models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'unique_together': {('name', 'creator')},
                'index_together': {('name', 'creator')},
            },
        ),
    ]