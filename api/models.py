import uuid

from ckeditor.fields import RichTextField
from django.contrib.auth.models import AbstractUser, UserManager
from django.core.exceptions import ValidationError
from django.db import models
from rest_framework_simplejwt.tokens import AccessToken
from django.utils import timezone
from strings import *


class BaseModel(models.Model):
    id = models.UUIDField(default=uuid.uuid4, editable=False, primary_key=True)
    created_at = models.DateTimeField(auto_now_add=True)
    modified_at = models.DateTimeField(auto_now=True)

    class Meta:
        abstract = True


class CustomUserManager(UserManager):
    def _create_user(self, email, password, **extra_fields):
        """
        Create and save a user with the given username, email, and password.
        """
        email = self.normalize_email(email)
        user = self.model(email=email, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_user(self, email=None, password=None, **extra_fields):
        extra_fields.setdefault('is_staff', False)
        extra_fields.setdefault('is_superuser', False)
        return self._create_user(email, password, **extra_fields)

    def create_superuser(self, email, password, **extra_fields):
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)

        if extra_fields.get('is_staff') is not True:
            raise ValueError('Superuser must have is_staff=True.')
        if extra_fields.get('is_superuser') is not True:
            raise ValueError('Superuser must have is_superuser=True.')

        return self._create_user(email, password, **extra_fields)
    
    # def get_users_with_valid_tokens(self):
    #     current_time = timezone.now()
    #     valid_user_ids = AccessToken.objects.filter(expires__gt=current_time).values_list('user', flat=True)
    #     valid_users = CustomUser.objects.filter(id__in=valid_user_ids)
    #     return valid_users


class CustomUser(AbstractUser):
    id = models.UUIDField(default=uuid.uuid4, editable=False, primary_key=True)
    username = models.CharField(
        max_length=250,
        db_index=True,
        unique=True,
        error_messages={"unique": "A user with this username already exists"},
        )
    email = models.EmailField()
    username = models.CharField(
        max_length=250,
        db_index=True,
        unique=True,
        error_messages={"unique": "A user with this username already exists"},
    )
    email = models.EmailField(
        error_messages={"unique": "A user with that email already exists"},
        unique=True,
        db_index=True
    )
    mobile_number = models.CharField(max_length=50, null=True, blank=True)
    is_online = models.BooleanField(default=False)
    # we store the datetime of the user's access token and 
    # this key is used when we fetch the users that are online through an endpoint
    token_expiry_datetime = models.DateTimeField(null=True, blank=True)
    USERNAME_FIELD = 'username'
    # USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = []
    objects = CustomUserManager()

    def save(self, *args, **kwargs):
        if self.mobile_number:
            if CustomUser.objects.filter(
                    mobile_number=self.mobile_number).exclude(id=self.id).exists():
                raise ValidationError(MOBILE_EXISTS)
        super().save(*args, **kwargs)

    def validate_unique(self, exclude=None):
        if not self.username.islower():
            self.username = self.username.lower()
        if not self.email.islower():
            self.email = self.email.lower()
        super().validate_unique(exclude=['id'])

    class Meta:
        ordering = ('first_name',)
        verbose_name_plural = 'Users'
        verbose_name = 'User'