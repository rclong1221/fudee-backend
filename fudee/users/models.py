from django.contrib.auth.models import AbstractUser
from django.urls import reverse
from django.utils.translation import gettext_lazy as _
from django.core.validators import MinValueValidator, MaxValueValidator
from django.core.exceptions import ValidationError
from django.db import models
import uuid as uuid_lib


class User(AbstractUser):
    """
    Default custom user model for My Awesome Project.
    If adding fields that need to be filled at user signup,
    check forms.SignupForm and forms.SocialSignupForms accordingly.
    """

    #: First and last name do not cover name patterns around the globe
    uuid = models.UUIDField( # Used by the API to look up the record 
        db_index=True,
        unique=True,
        default=uuid_lib.uuid4,
        editable=False)
    name = models.CharField(_("Name of User"), blank=True, max_length=255)
    first_name = models.CharField(_("First Name"), blank=True, max_length=255)
    last_name = models.CharField(_("Last Name"), blank=True, max_length=255)
    middle_name = models.CharField(_("Middle Name"), blank=True, max_length=255)
    is_active = models.BooleanField(default=True)
    date_updated = models.DateTimeField(auto_now_add=True)
    primary_image = models.UUIDField(blank=True, null=True)

    def get_absolute_url(self):
        """Get url for user's detail view.

        Returns:
            str: URL for user detail.

        """
        return reverse("users:detail", kwargs={"username": self.username})
    
    def soft_delete(self):
        self.is_active = False
        self.save()
    
    def __str__(self):
        return "{0}".format(self.name)

class UserImage(models.Model):
    """
    
    """
    uuid = models.UUIDField( # Used by the API to look up the record 
        db_index=True,
        unique=True,
        default=uuid_lib.uuid4,
        editable=False)
    image = models.ImageField(blank=True, null=True)
    user = models.ForeignKey(User, on_delete=models.PROTECT)
    date_created = models.DateTimeField(auto_now_add=True, blank=True)
    
    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)  # Call the "real" save() method.
        u = None
        
        try:
            u = User.objects.get(uuid=self.user.uuid)
        except User.DoesNotExist:
            return
        
        u.primary_image = self.uuid
        u.save()