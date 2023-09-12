import json

from django.contrib.auth.hashers import make_password
from django.http import QueryDict
from rest_framework import serializers
from rest_framework.validators import UniqueValidator

from api.models import CustomUser
from base.utils import custom_password_validator
from strings import *



class CustomPasswordField(serializers.CharField):
    def __init__(self, **kwargs):
        self.required = False
        self.validators.append(custom_password_validator)
        super().__init__(**kwargs)

    def to_internal_value(self, data):
        data = make_password(data)
        return super().to_internal_value(data)


class CustomEmailField(serializers.EmailField):
    def to_internal_value(self, data):
        data = data.lower()
        return super().to_internal_value(data)


class CustomListField(serializers.ListField):
    def to_internal_value(self, data):
        if isinstance(self.context["request"].data, QueryDict):
            data = data[0]
        if isinstance(data, str):
            data = json.loads(data)
        return super().to_internal_value(data)


class TextSerializer(serializers.Serializer):
    text = serializers.CharField()
    modified_on = serializers.DateTimeField(read_only=True)
    document = serializers.FileField(required=False)

    def create(self, validated_data):
        instance = self.context["model"](**validated_data)
        instance.save()
        return instance


class CustomUserSerializer(serializers.ModelSerializer):
    password = serializers.CharField(max_length=100, required=False)
    email = CustomEmailField(
        max_length=254,
        validators=[UniqueValidator(
            queryset=CustomUser.objects.all(),
            message=EMAIL_EXISTS,
            lookup='iexact'
            )]
        )
    password = CustomPasswordField()

    class Meta:
        model = CustomUser
        fields = (
            'username',
            'id',
            'password',
            'date_joined',
            'first_name',
            'last_name',
            'email',
            'mobile_number',
            'is_superuser',
            'last_login',
            'token_expiry_datetime',
        )
        read_only_fields = (
            'date_joined',
            'last_login',
            'is_superuser',
        )

    def validate_mobile_number(self, value):
        if value:
            value = phonenumber_validator(value)
        return value

    def update(self, instance, validated_data):
        if validated_data.get('mobile_number'):
            if validated_data.get('mobile_number') != instance.mobile_number:
                validated_data['is_mobile_verified'] = False
        if validated_data.get('email'):
            if validated_data.get('email') != instance.email:
                validated_data['is_email_verified'] = False
        return super().update(instance, validated_data)

    def to_representation(self, instance):
        data = super().to_representation(instance)
        data.pop('password')
        return data


class UserPasswordSerializer(serializers.ModelSerializer):
    password = CustomPasswordField(required=True)

    class Meta:
        model = CustomUser
        fields = ("password",)

