import uuid
from django.contrib.auth import get_user_model
from rest_framework import serializers
from fudee.organizations.models import Organization
    
from phonenumber_field.modelfields import PhoneNumberField
from datetime import datetime

User = get_user_model()