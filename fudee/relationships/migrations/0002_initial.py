# Generated by Django 3.2.13 on 2022-07-23 17:02

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('relationships', '0001_initial'),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.AddField(
            model_name='usergroupuser',
            name='updater',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.PROTECT, related_name='usergroupuser_updater', to=settings.AUTH_USER_MODEL),
        ),
        migrations.AddField(
            model_name='usergroupuser',
            name='user',
            field=models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, to=settings.AUTH_USER_MODEL),
        ),
        migrations.AddField(
            model_name='usergroupimage',
            name='user_group',
            field=models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, to='relationships.usergroup'),
        ),
        migrations.AddField(
            model_name='usergroup',
            name='creator',
            field=models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, to=settings.AUTH_USER_MODEL),
        ),
        migrations.AddField(
            model_name='relationship',
            name='updater',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.PROTECT, related_name='relationship_updater', to=settings.AUTH_USER_MODEL),
        ),
        migrations.AddField(
            model_name='relationship',
            name='user1',
            field=models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, related_name='Friend_user1', to=settings.AUTH_USER_MODEL),
        ),
        migrations.AddField(
            model_name='relationship',
            name='user2',
            field=models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, related_name='Friend_user2', to=settings.AUTH_USER_MODEL),
        ),
        migrations.AddField(
            model_name='invite',
            name='user',
            field=models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, related_name='invite_from_user', to=settings.AUTH_USER_MODEL),
        ),
        migrations.AlterUniqueTogether(
            name='usergroupuser',
            unique_together={('group', 'user')},
        ),
        migrations.AlterIndexTogether(
            name='usergroupuser',
            index_together={('group', 'user')},
        ),
        migrations.AlterUniqueTogether(
            name='usergroup',
            unique_together={('name', 'creator')},
        ),
        migrations.AlterIndexTogether(
            name='usergroup',
            index_together={('name', 'creator')},
        ),
        migrations.AlterUniqueTogether(
            name='relationship',
            unique_together={('user1', 'user2')},
        ),
        migrations.AlterIndexTogether(
            name='relationship',
            index_together={('user1', 'user2')},
        ),
    ]
