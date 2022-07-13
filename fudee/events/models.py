from django.db import models
from django.contrib.auth import get_user_model
from django.core.validators import MinValueValidator, MaxValueValidator
from django.core.exceptions import ValidationError
from django.utils.translation import gettext_lazy as _

import uuid as uuid_lib

from datetime import datetime
from recurrence.fields import RecurrenceField

User = get_user_model()

class Event(models.Model):
    uuid = models.UUIDField(
        db_index=True,
        unique=True,
        default=uuid_lib.uuid4,
        editable=False)
    title = models.CharField(max_length=254, blank=False, null=False)
    description = models.TextField(blank=True, null=True)
    location = models.CharField(max_length=254, blank=True, null=True)
    primary_image = models.UUIDField(blank=True, null=True)
    user = models.ForeignKey(User, related_name="event_user", on_delete=models.PROTECT)
    date_start = models.DateTimeField(blank=False, null=False)
    date_end = models.DateTimeField(blank=True, null=True)
    recurrences = RecurrenceField()
    date_created = models.DateField(auto_now_add=True, blank=True)
    date_updated = models.DateField(blank=True, null=True)
    updater_id = models.IntegerField(blank=True, null=True)