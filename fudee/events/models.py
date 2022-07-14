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
    recurrences = RecurrenceField(blank=True)
    date_created = models.DateField(auto_now_add=True, blank=True)
    date_updated = models.DateField(blank=True, null=True)
    updater_id = models.IntegerField(blank=True, null=True)

class EventUser(models.Model):
    """
    
    """
    uuid = models.UUIDField( # Used by the API to look up the record 
        db_index=True,
        unique=True,
        default=uuid_lib.uuid4,
        editable=False)
    event = models.ForeignKey(Event, on_delete=models.PROTECT)
    user = models.ForeignKey(User, on_delete=models.PROTECT)
    access = models.IntegerField(default=0, validators=[MinValueValidator(0), MaxValueValidator(2)])
    is_active = models.BooleanField(default=False, blank=False, null=False)
    date_created = models.DateField(auto_now_add=True, blank=True)
    date_accepted = models.DateField(blank=True, null=True)
    date_updated = models.DateField(blank=True, null=True)
    updater_id = models.IntegerField(blank=True, null=True)
    
    def clean(self):
        if self.updater_id is None:
            pass
        elif self.updater_id != self.user.id:
            raise ValidationError("Updater ID is invalid.")
    
    class Meta:
        unique_together = (('event', 'user'),)
        index_together = (('event', 'user'),)

class EventImage(models.Model):
    """
    
    """
    uuid = models.UUIDField( # Used by the API to look up the record 
        db_index=True,
        unique=True,
        default=uuid_lib.uuid4,
        editable=False)
    image = models.ImageField(blank=True, null=True)
    event = models.ForeignKey(Event, on_delete=models.PROTECT)
    date_created = models.DateTimeField(auto_now_add=True, blank=True)
    
    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)
        event = None
        
        try:
            event = Event.objects.get(uuid=self.event.uuid)
        except self.queryset.DoesNotExist:
            return
        
        event.primary_image = self.uuid
        event.save()

class EventParam(models.Model):
    uuid = models.UUIDField(
        db_index=True,
        unique=True,
        default=uuid_lib.uuid4,
        editable=False)
    event = models.ForeignKey(Event, related_name='params', on_delete=models.PROTECT)
    param = models.CharField(max_length=16)
    value = models.IntegerField()
    index = models.IntegerField(default=0)