from django.db.models import Q
from rest_framework import serializers

from utils.utils import Utils
from ICD10.models.user import User
from constants.constants import Constants
from validators.validator import Validator


class UserSerializer(serializers.ModelSerializer):

    created_at = serializers.DateTimeField(read_only=True)
    password = serializers.CharField(write_only=True, required=True, min_length=8)
   
    # permissions = serializer.SerializerMethodField()
    class Meta:
        model = User
        fields = [
            "id",
            "username",
            "first_name",
            "last_name",
            "email",
            "avatar",
            "role",
            "is_staff",
            "is_superuser",
            "status",
            "is_verified_doctor",
            "license_number",
            "hospital",
            "verification_file",
            "created_at",
            "password",
        ]

    def create(self, validated_data):
        request = self.context.get("request")
        is_first_user = not User.objects.exists()
        password = validated_data.pop("password")

         # Dữ liệu cơ bản
        email = validated_data.get("email")
        username = validated_data.get("username")


        user = User(
            **validated_data,
            is_superuser=is_first_user,
            is_staff=is_first_user,
        )
        
        user.set_password(password)  # ✅ Hash password
        
        if is_first_user:
            user.role = 3
        else:
            user.role = 1

        user.save()
        return user

    def update(self, instance, validated_data):
        request = self.context.get("request")
        
        instance.updated_at = Utils.get_current_datetime()
        if self.context.get(Constants.REGISTER, False):
            instance.status = 1

        if "password" in validated_data:
            instance.set_password(validated_data.pop("password"))


        if "groups" in validated_data:
            groups = validated_data.pop("groups")
            instance.groups.set(groups)

        for attr, value in validated_data.items():
            if attr in ["created_at"]:   
                continue
            setattr(instance, attr, value)
            
        # Đảm bảo các trường is_staff, is_superuser đã đúng trước khi gán role
        #instance.refresh_from_db()
        
        if instance.is_superuser:
            instance.role = 3  # admin
        elif instance.is_verified_doctor:
            instance.role = 1 # doctor
        else:
            instance.role = 2  # user

        instance.save()
        return instance

    def validate(self, data):
        errors = {}
        if self.instance is None:


            if self.context.get(Constants.ADMIN_REGISTER_USER, False):
                if not data.get("email"):
                    errors["email"] = "Email field is required."
                if not data.get("username"):
                    errors["username"] = "Username field is required."
             

        else:
            if self.context.get(Constants.REGISTER, False):
                if not data.get("password") :
                    errors["password"] = "Password field is required."
                # if not data.get("fullname"):
                #     errors["fullname"] = "Fullname field is required."
                # if not data.get("phone"):
                #     errors["phone"] = "Phone field is required."



        if errors:
            raise serializers.ValidationError(errors)

        return data

    def validate_avatar(self, value):
        # avatar không bắt buộc
        if not value:
            return None
        if isinstance(value, str):
            if value.startswith('data:image/'):  # Nếu là base64
                return Validator.validate_avatar_base64(value)
            else:  # Nếu là URL
                return Validator.validate_avatar(value)
        else:  # Nếu là file upload
            return Validator.validate_avatar_file(value)
    
    def validate_email(self, value):
        if value:
            return Validator.validate_email(value)
        return value
    
    