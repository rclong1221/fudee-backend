from django.db import models
from django.contrib.auth import get_user_model
from django.core.validators import MinValueValidator, MaxValueValidator
from django.core.exceptions import ValidationError
from django.utils.translation import gettext_lazy as _

import uuid as uuid_lib

from datetime import datetime
from fudee.organizations.models import Organization
from fudee.events.models import Event

User = get_user_model()

class Shift(models.Model):
    uuid = models.UUIDField(
        db_index=True,
        unique=True,
        default=uuid_lib.uuid4,
        editable=False)
    employee = models.ForeignKey(User, related_name="employee", on_delete=models.PROTECT, blank=True, null=True)
    organization = models.ForeignKey(Organization, related_name="organization", on_delete=models.PROTECT, blank=True, null=True)
    event = models.ForeignKey(Event, related_name="event", on_delete=models.PROTECT)
    date_created = models.DateField(auto_now_add=True, blank=True)
    date_updated = models.DateField(blank=True, null=True)
    updater_id = models.IntegerField(blank=True, null=True)

class Swap(models.Model):
    uuid = models.UUIDField(
        db_index=True,
        unique=True,
        default=uuid_lib.uuid4,
        editable=False)
    old_employee = models.ForeignKey(User, related_name="old_employee", on_delete=models.PROTECT)
    new_employee = models.ForeignKey(User, related_name="new_employee", on_delete=models.PROTECT, blank=True, null=True)
    shift = models.ForeignKey(Shift, related_name="shift", on_delete=models.PROTECT)
    is_approved = models.BooleanField(default=False)
    date_created = models.DateField(auto_now_add=True, blank=True)
    date_updated = models.DateField(blank=True, null=True)
    manager = models.ForeignKey(User, related_name="manager", on_delete=models.PROTECT, blank=True, null=True)