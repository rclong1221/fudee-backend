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
    updater = models.ForeignKey(User, related_name="shift_updater", on_delete=models.PROTECT, blank=True, null=True)
    
    # def clean(self):
    #     if not self.name:
    #         raise ValidationError("Valid organization name is required.")
    
    class Meta:
        unique_together = (('employee', 'event'),)
        index_together = (('employee', 'event'),)

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
    
    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)  # Call the "real" save() method.
        if self.is_approved:
            shift = None
            
            try:
                shift = Shift.objects.get(uuid=self.shift.uuid)
            except Shift.DoesNotExist:
                return
            
            shift.employee = self.new_employee
            shift.save()
    
    class Meta:
        unique_together = (('old_employee', 'shift'),)
        index_together = (('old_employee', 'shift'),)