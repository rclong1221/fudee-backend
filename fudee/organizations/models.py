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
    user = models.ForeignKey(User, related_name="invite_from_user", on_delete=models.PROTECT)
    email = models.EmailField(max_length=254, blank=True)
    phone = PhoneNumberField(blank=True)
    accepted = models.BooleanField(default=False)
    date_created = models.DateField(auto_now_add=True, blank=True)
    
    def clean(self):
        if not self.email and not self.phone:
            raise ValidationError("Email address or phone number is required.")