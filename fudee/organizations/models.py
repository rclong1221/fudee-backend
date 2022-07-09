from django.db import models
from django.contrib.auth import get_user_model
from django.core.validators import MinValueValidator, MaxValueValidator
from django.core.exceptions import ValidationError
from django.utils.translation import gettext_lazy as _

import uuid as uuid_lib

from phonenumber_field.modelfields import PhoneNumberField
from datetime import datetime

User = get_user_model()

class Organization(models.Model):
    """
    
    """
    uuid = models.UUIDField( # Used by the API to look up the record 
        db_index=True,
        unique=True,
        default=uuid_lib.uuid4,
        editable=False)
    name = models.CharField(max_length=254, blank=False, null=False)
    image = models.FileField(blank=True, null=True)
    date_created = models.DateField(auto_now_add=True, blank=True)
    date_updated = models.DateField(blank=True, null=True)
    updater_id = models.IntegerField(blank=True, null=True)
    
    def clean(self):
        if not self.name:
            raise ValidationError("Valid organization name is required.")

class OrganizationUser(models.Model):
    """
    
    """
    uuid = models.UUIDField( # Used by the API to look up the record 
        db_index=True,
        unique=True,
        default=uuid_lib.uuid4,
        editable=False)
    organization = models.ForeignKey(Organization, on_delete=models.PROTECT)
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
        unique_together = (('organization', 'user'),)
        index_together = (('organization', 'user'),)