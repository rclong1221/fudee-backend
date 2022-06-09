from django.db import models
from django.contrib.auth import get_user_model

import uuid as uuid_lib

from phonenumber_field.modelfields import PhoneNumberField
from datetime import datetime

User = get_user_model()

class Invite(models.Model):
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
        
class Relationship(models.Model):
    uuid = models.UUIDField( # Used by the API to look up the record 
        db_index=True,
        unique=True,
        default=uuid_lib.uuid4,
        editable=False)
    
    user1 = models.ForeignKey(User, related_name="Friend_user1", on_delete=models.PROTECT)
    user2 = models.ForeignKey(User, related_name="Friend_user2", on_delete=models.PROTECT)
    relationship = models.IntegerField(validators=[MinValueValidator(-1), MaxValueValidator(2)])
    date_created = models.DateField(auto_now_add=True, blank=True)
    date_accepted = models.DateField(blank=True, null=True)
    date_updated = models.DateField(blank=True, null=True)
    updater_id = models.IntegerField(blank=True, null=True)
    
    def clean(self):
        if self.user1.id == self.user2.id:
            raise ValidationError("User cannot have a relationship with themself.")
        
        if self.updater_id is None:
            pass
        elif self.updater_id != self.user1.id and self.updater_id != self.user2.id:
            raise ValidationError("Updater ID is invalid.")
    
    class Meta:
        unique_together = (('user1', 'user2'),)
        index_together = (('user1', 'user2'),)