import base64
import math
import os
import io
import traceback
import urllib
import mimetypes
from urllib.request import urlopen
import random
import string
import magic
import secrets
import six
import logging
import pytz
import hashlib
import hmac
from collections import OrderedDict
import json
import requests
from io import BytesIO

import phonenumbers
from django.conf import settings
from django.contrib.auth.password_validation import \
    get_default_password_validators
from django.core.exceptions import ValidationError
from django.core.files.base import ContentFile
from django.core.files.uploadedfile import TemporaryUploadedFile
from django.core.paginator import InvalidPage
from django.db.models import IntegerField, Subquery
from django.http import QueryDict
from django.utils import timezone
from rest_framework import serializers, status
from rest_framework.pagination import (LimitOffsetPagination,
                                       PageNumberPagination)
from rest_framework.response import Response
from rest_framework_simplejwt.tokens import RefreshToken
from cryptography.fernet import Fernet
from rest_framework_simplejwt.tokens import AccessToken
from datetime import datetime


logger = logging.getLogger('__name__')


class CustomException(Exception):
    pass

def get_dict_data(data):
    if isinstance(data, dict):
        return data
    else:
        return data.dict()


def custom_password_validator(password, user=None, password_validators=None):
    errors = []
    if not password:
        errors.append('Password cannot contain blank space')

    if password_validators is None:
        password_validators = get_default_password_validators()

    for validator in password_validators:
        try:
            validator.validate(password, user)
        except ValidationError as error:
            errors.extend(error.messages)

    if errors:
        if user:
            raise ValidationError({'password': errors})
        else:
            raise ValidationError(errors)

class CustomLimitOffsetPagination(LimitOffsetPagination):
    max_limit = 100


class CustomPagination(PageNumberPagination):
    def get_paginated_response(self, data):
        return Response(OrderedDict([
            ('count', self.page.paginator.count),
            ('next', self.get_next_link()),
            ('previous', self.get_previous_link()),
            ('total_pages', math.ceil(self.page.paginator.count / self.page_size)),
            ('data', data)
        ]))

    def paginate_queryset(self, queryset, request, view=None):
        """
        Paginate a queryset if required, either returning a
        page object, or `None` if pagination is not configured for this view.
        """
        page_size = self.get_page_size(request)
        if not page_size:
            return None

        paginator = self.django_paginator_class(queryset, page_size)
        page_number = request.query_params.get(self.page_query_param, 1)
        if page_number in self.last_page_strings:
            page_number = paginator.num_pages

        try:
            self.page = paginator.page(page_number)
        except InvalidPage as exc:
            msg = self.invalid_page_message.format(
                page_number=page_number, message=six.text_type(exc)
            )
            raise InvalidPage(msg)

        if paginator.num_pages > 1 and self.template is not None:
            # The browsable API should display pagination controls.
            self.display_page_controls = True

        self.request = request
        return list(self.page)


def paginated_success_response(data, message=None):
    return Response({'status': {'code': status.HTTP_200_OK,
                                'message': message},
                     **data})


def success_response(data=None, message=None, request=None, extra_data={}):
    result = {'status': {'code': status.HTTP_200_OK,
                         'message': message},
              'data': data
              }
    result.update(extra_data)
    return Response(result)


def error_response(data=None, message=None, request=None, code=status.HTTP_403_FORBIDDEN):
    return Response({'status': {'code': code,
                                'message': message},
                     'data': data
                     })



def get_jwt_auth_token(user):
    refresh = RefreshToken.for_user(user)

    return {
        'refresh': str(refresh),
        'access': str(refresh.access_token),
    }

def is_token_valid(user):
    # Get the user's token
    user_token = AccessToken.for_user(user)
    # Check if the token has expired
    token_expired = user_token['exp'] < datetime.now().timestamp()
    return not token_expired



def get_boolean(x):
    if type(x) == bool:
        return x
    if x:
        if x.lower() == 'true' or x == 1 or x == '1' or x == 't':
            return True
        else:
            return False
    else:
        return False




