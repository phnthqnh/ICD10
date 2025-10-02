from django.db import models
from django.contrib.auth.models import Group, Permission
from django.contrib.auth.hashers import make_password, check_password
from constants.constants import Constants
from django.contrib.auth.models import (
    AbstractBaseUser,
    PermissionsMixin,
    BaseUserManager,
)
from django.utils import timezone

    

class UserManager(BaseUserManager):
    def create_user(self, username, email, password=None, **extra_fields):
        if not email:
            raise ValueError("Users must have an email address")
        email = self.normalize_email(email)
        user = self.model(username=username, email=email, **extra_fields)

        if password:
            user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, username, email, password, **extra_fields):
        extra_fields.setdefault("is_staff", True)
        extra_fields.setdefault("is_superuser", True)
        extra_fields.setdefault("status", 1)

        if extra_fields.get("is_staff") is not True:
            raise ValueError("Superuser must have is_staff=True.")
        if extra_fields.get("is_superuser") is not True:
            raise ValueError("Superuser must have is_superuser=True.")
        user = self.create_user(username, email, password, **extra_fields)
        user.user_permissions.set(Permission.objects.all())
        user.save()

        return user

class User(AbstractBaseUser, PermissionsMixin):
    objects = UserManager()
    all_objects = models.Manager()
    username = models.CharField(max_length=150, unique=True)
    first_name = models.CharField(max_length=255, null=True, blank=True)
    last_name = models.CharField(max_length=255, null=True, blank=True)
    avatar = models.TextField(null=True, blank=True)
    email = models.EmailField(unique=True)
    password = models.CharField(max_length=128, null=True)
    status = models.PositiveSmallIntegerField(choices=Constants.USER_STATUS, default=3)
    email_verified = models.BooleanField(default=False)
    is_staff = models.BooleanField(default=False)
    is_superuser = models.BooleanField(default=False)
    last_login = models.DateTimeField(null=True)
    role = models.IntegerField(choices=Constants.ROLE, default=1)
    
    is_verified_doctor = models.BooleanField(default=False)
    # Thông tin xác minh
    license_number = models.CharField(max_length=50, null=True, blank=True)
    hospital = models.CharField(max_length=255, null=True, blank=True)
    verification_file = models.TextField(null=True, blank=True)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(null=True)

    groups = models.ManyToManyField(
        Group,
        related_name="custom_users",
        blank=True,
    )

    user_permissions = models.ManyToManyField(
        Permission, related_name="custom_users", blank=True
    )

  
    USERNAME_FIELD = "username"
    EMAIL_FIELD = "email"

    def set_password(self, raw_password):
        self.password = make_password(raw_password)

    def check_password(self, raw_password):
        return check_password(raw_password, self.password)
    

    def __str__(self):
        return self.username

    class Meta:
        app_label = "ICD10"
        db_table = "user"

    @property
    def is_authenticated(self):
        return self.status


