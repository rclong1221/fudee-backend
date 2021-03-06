# Generated by Django 3.2.13 on 2022-07-23 17:02

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('events', '0001_initial'),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.AddField(
            model_name='eventuser',
            name='updater',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.PROTECT, related_name='eventuser_updater', to=settings.AUTH_USER_MODEL),
        ),
        migrations.AddField(
            model_name='eventuser',
            name='user',
            field=models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, to=settings.AUTH_USER_MODEL),
        ),
        migrations.AddField(
            model_name='eventparam',
            name='event',
            field=models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, related_name='params', to='events.event'),
        ),
        migrations.AddField(
            model_name='eventimage',
            name='event',
            field=models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, to='events.event'),
        ),
        migrations.AddField(
            model_name='event',
            name='updater',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.PROTECT, related_name='event_updater', to=settings.AUTH_USER_MODEL),
        ),
        migrations.AddField(
            model_name='event',
            name='user',
            field=models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, related_name='event_user', to=settings.AUTH_USER_MODEL),
        ),
        migrations.AlterUniqueTogether(
            name='eventuser',
            unique_together={('event', 'user')},
        ),
        migrations.AlterIndexTogether(
            name='eventuser',
            index_together={('event', 'user')},
        ),
    ]
