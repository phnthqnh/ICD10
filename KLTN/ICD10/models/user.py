from django.db import models
from django.contrib.auth.models import Group, Permission
from django.contrib.auth.hashers import make_password, check_password
from constants.constants import Constants
from django.contrib.auth.models import (
    AbstractBaseUser,
    PermissionsMixin,
    BaseUserManager,
)
from django.utils.html import format_html

    

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
    avatar = models.URLField(null=True, blank=True)
    email = models.EmailField(unique=True)
    password = models.CharField(max_length=128, null=True)
    status = models.PositiveSmallIntegerField(choices=Constants.USER_STATUS, default=3)
    email_verified = models.BooleanField(default=False)
    pending_email = models.EmailField(null=True, blank=True)
    pending_email_verified = models.BooleanField(default=False)
    pending_email_token = models.CharField(max_length=255, null=True, blank=True)
    is_staff = models.BooleanField(default=False)
    is_superuser = models.BooleanField(default=False)
    last_login = models.DateTimeField(null=True)
    role = models.IntegerField(choices=Constants.ROLE, default=1)
    
    is_verified_doctor = models.BooleanField(default=False)
    # Thông tin xác minh
    license_number = models.CharField(max_length=50, null=True, blank=True)
    hospital = models.CharField(max_length=255, null=True, blank=True)
    verification_file = models.URLField(null=True, blank=True)
    
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
        verbose_name = 'Người dùng'
        verbose_name_plural = 'Người dùng'
        app_label = "ICD10"
        db_table = "user"

    @property
    def is_authenticated(self):
        return self.status
    
    def verification_image_tag(self):
        if not self.verification_file:
            return "—"
        return format_html("""
            <img src="{0}" style="max-height: 200px; cursor:pointer; border:1px solid #ccc; padding:4px;"
                onclick="document.getElementById('imgModal').style.display='block';
                        document.getElementById('imgModalContent').src='{0}'" />

            <div id="imgModal" style="
                display:none; position:fixed; z-index:9999; padding-top:100px;
                left:0; top:0; width:100%; height:100%; overflow:auto;
                background-color:rgba(0,0,0,0.8);">
                <span onclick="document.getElementById('imgModal').style.display='none'"
                    style="position:absolute; top:30px; right:50px; font-size:40px; color:white; cursor:pointer;">
                    &times;
                </span>
                <img id="imgModalContent" style="margin:auto; display:block; max-width:90%; max-height:90%;">
            </div>
            """, self.verification_file
        )

    verification_image_tag.short_description = "Xem ảnh"
    
    def avatar_tag(self):
        if not self.avatar:
            return "—"
        return format_html("""
            <img src="{0}" style="max-height: 200px; cursor:pointer; border:1px solid #ccc; padding:4px;"
                onclick="document.getElementById('imgModal').style.display='block';
                        document.getElementById('imgModalContent').src='{0}'" />

            <div id="imgModal" style="
                display:none; position:fixed; z-index:9999; padding-top:100px;
                left:0; top:0; width:100%; height:100%; overflow:auto;
                background-color:rgba(0,0,0,0.8);">
                <span onclick="document.getElementById('imgModal').style.display='none'"
                    style="position:absolute; top:30px; right:50px; font-size:40px; color:white; cursor:pointer;">
                    &times;
                </span>
                <img id="imgModalContent" style="margin:auto; display:block; max-width:90%; max-height:90%;">
            </div>
            """, self.avatar
        )

    avatar_tag.short_description = "Xem ảnh"


