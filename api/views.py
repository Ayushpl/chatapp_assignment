import json
from django.conf import settings
from django.contrib.auth import authenticate,logout
from django.contrib.auth.hashers import check_password
from django.db import transaction
from django.http import JsonResponse
from django.utils import timezone
from django.views.generic.list import BaseListView

from rest_framework import status
from rest_framework.permissions import AllowAny
from rest_framework.views import APIView
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework_simplejwt.authentication import AUTH_HEADER_TYPES
from rest_framework_simplejwt.backends import TokenBackend
from rest_framework_simplejwt.exceptions import InvalidToken
from rest_framework_simplejwt.serializers import TokenRefreshSerializer
from rest_framework.views import APIView
from rest_framework import status
from django.db.models import Q

from base.base_views import (CustomAPIView, CustomCreateModelMixin, CustomGenericView)
from api.models import  CustomUser
from base.utils import (CustomException, error_response, success_response)
from api.models import (CustomUser)
from base.utils import (CustomException, error_response, success_response)
from api.serializers import (CustomUserSerializer,
                             UserPasswordSerializer)
from strings import *
from base.utils import get_jwt_auth_token


class PasswordAPI(CustomAPIView):
    def initial(self, request, *args, **kwargs):
        if request.method in ('GET', 'POST'):
            self.permission_classes = (AllowAny,)
        super().initial(request, *args, **kwargs)

    def get(self, request):
        user = CustomUser.objects.only('id', 'email', 'first_name', 'last_name').filter(
            email__iexact=request.query_params['email']).first()
        if user is not None:
            token = TokenBackend(
                settings.SIMPLE_JWT['ALGORITHM'],
                settings.SIMPLE_JWT['SIGNING_KEY']).encode({
                'email': user.email.lower(),
                'exp': int((timezone.now() + timezone.timedelta(days=1)).timestamp())
            })
            return success_response(message=RESET_PASSWORD_LINK_SENT)
        return error_response(message=EMAIL_NOT_EXISTS)

    def post(self, request):
        token = request.data['token']
        user_data = TokenBackend(
            settings.SIMPLE_JWT['ALGORITHM'],
            settings.SIMPLE_JWT['SIGNING_KEY']).decode(token)
        if user_data['exp'] < timezone.now().timestamp():
            raise CustomException(EXPIRED_LINK)
        user = CustomUser.objects.get(email__iexact=user_data['email'])
        serializer = UserPasswordSerializer(instance=user, data=request.data, context={'request': request})
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return success_response(message=PASSWORD_UPDATED)

    @transaction.atomic
    def put(self, request):
        if not check_password(request.data['old_password'], request.user.password):
            raise CustomException(OLD_PASSWORD_WRONG)
        if request.data['password'] == request.data['old_password']:
            raise CustomException(SAME_PASSWORD_ERROR)
        serializer = UserPasswordSerializer(instance=request.user, data=request.data, context={'request': request})
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return success_response(message=PASSWORD_UPDATED)


class RegistrationView(CustomCreateModelMixin, CustomGenericView):

    serializer_class = CustomUserSerializer
    queryset = CustomUser.objects.all()
    throttle_scope = 'on_boarding'
    permission_classes = (AllowAny,)

    @transaction.atomic
    def post(self, request):
        serializer = CustomUserSerializer(data=request.data, context={
                                          'request': request, 'view': self})
        serializer.is_valid(raise_exception=True)
        user = serializer.save()
        token = TokenBackend(
            settings.SIMPLE_JWT['ALGORITHM'],
            settings.SIMPLE_JWT['SIGNING_KEY']).encode({
                'email': user.email,
                'exp': int((timezone.now() + timezone.timedelta(days=1)).timestamp())
            })
        return success_response(data=serializer.data, extra_data={'token': get_jwt_auth_token(user)})


# class LoginView(CustomAPIView):
#     permission_classes = (AllowAny,)

#     @transaction.atomic
#     def post(self, request):
#         user = authenticate(
#             request,
#             username=request.data['email'].lower(),
#             password=request.data['password']
#         )

#         if user is None:
#             return error_response(message=CANNOT_LOGIN, code=status.HTTP_401_UNAUTHORIZED)

#         CustomUser.objects.filter(id=user.id).update(last_login=timezone.now())
#         user_serializer = CustomUserSerializer(
#             user, context={'request': request})
#         return success_response(data=user_serializer.data, message=LOGIN_SUCCESS, extra_data={'token': get_jwt_auth_token(user) })


# class ConvertTokenAPIView(ConvertTokenView):
#     permission_classes = (AllowAny,)

#     def post(self, request):
#         url, headers, body, status = self.create_token_response(request._request)
#         if status != 200:
#             raise AuthenticationFailed()
#         token_data = json.loads(body)
#         user = get_access_token_model().objects.filter(token=token_data['access_token']).first().user
#         user_serializer = CustomUserSerializer(user, context={'request': request})
#         return success_response(data=user_serializer.data, message=LOGIN_SUCCESS, extra_data={'token': token_data})


class LoginAPI(CustomAPIView):
    permission_classes = (AllowAny,)

    def post(self, request):
        user = authenticate(
            request,
            username=request.data['username'].lower(),
            password=request.data['password']
        )
        if user is None:
            return error_response(message=CANNOT_LOGIN, code=status.HTTP_401_UNAUTHORIZED)
        
        #setting is_online to True when user logs in
        print(timezone.now())
        user_token_expiry_datetime = timezone.now() + timezone.timedelta(days=1)
        CustomUser.objects.filter(id=user.id).update(last_login=timezone.now(),is_online=True,token_expiry_datetime=user_token_expiry_datetime)
        user_data = CustomUserSerializer(user, context={'request': request}).data
        return success_response(data=user_data, message=LOGIN_SUCCESS, extra_data={'token': get_jwt_auth_token(user)})

class LogoutView(CustomAPIView):
    @transaction.atomic
    def post(self, request):
        #setting is_online to false when user logs out
        CustomUser.objects.filter(id=request.user.id).update(is_online=False)
        refresh_token = request.data["refresh_token"]
        logout(request)
        try:
            token = RefreshToken(refresh_token)
            token.blacklist()
            return success_response(message=LOGOUT_SUCCESS)
        except Exception as e:
            return success_response(message=LOGOUT_SUCCESS)

# class RegistrationView(CustomAPIView):
#     permission_classes = (AllowAny,)
#     throttle_scope = 'on_boarding'

#     @transaction.atomic
#     def post(self, request):
#         serializer = CustomUserSerializer(data=request.data, context={'request': request, 'view': self})
#         serializer.is_valid(raise_exception=True)
#         user = serializer.save()

#         token = TokenBackend(
#             settings.SIMPLE_JWT['ALGORITHM'],
#             settings.SIMPLE_JWT['SIGNING_KEY']).encode({
#             'email': user.email,
#             'exp': int((timezone.now() + timezone.timedelta(days=1)).timestamp())
#         })
#         return success_response(data=serializer.data, extra_data={'token': get_jwt_auth_token(user)})



# class LoginAPI(CustomAPIView):
#     permission_classes = (AllowAny,)

#     def post(self, request):
#         user = authenticate(
#             request,
#             username=request.data['username'].lower(),
#             password=request.data['password']
#         )
#         if user is None:
#             return error_response(message=CANNOT_LOGIN, code=status.HTTP_401_UNAUTHORIZED)
#         CustomUser.objects.filter(id=user.id).update(last_login=timezone.now())
#         user_data = CustomUserSerializer(user, context={'request': request}).data
#         return success_response(data=user_data, message=LOGIN_SUCCESS)


class RegistrationView(CustomAPIView):
    permission_classes = (AllowAny,)
    throttle_scope = 'on_boarding'

    @transaction.atomic
    def post(self, request):
        serializer = CustomUserSerializer(data=request.data, context={'request': request, 'view': self})
        serializer.is_valid(raise_exception=True)
        user = serializer.save()

        token = TokenBackend(
            settings.SIMPLE_JWT['ALGORITHM'],
            settings.SIMPLE_JWT['SIGNING_KEY']).encode({
            'email': user.email,
            'exp': int((timezone.now() + timezone.timedelta(days=1)).timestamp())
        })
        return success_response(data=serializer.data)



class RefreshTokenView(CustomGenericView):
    permission_classes = ()
    authentication_classes = ()
    serializer_class = TokenRefreshSerializer
    www_authenticate_realm = 'api'

    def get_authenticate_header(self, request):
        return '{0} realm="{1}"'.format(
            AUTH_HEADER_TYPES[0],
            self.www_authenticate_realm,
        )

    def post(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        try:
            serializer.is_valid(raise_exception=True)
            user_data = TokenBackend(
                settings.SIMPLE_JWT['ALGORITHM'],
                settings.SIMPLE_JWT['SIGNING_KEY']).decode(serializer.validated_data['access'])
            user = CustomUser.objects.get(id=user_data['user_id'])
            if not user.is_active:
                raise Exception(USER_NOT_ACTIVE)
        except Exception as e:
            raise InvalidToken(str(e))
        return success_response(extra_data=serializer.validated_data)
    
    
# from django.contrib.auth.models import AnonymousUser
# from rest_framework_simplejwt.views import TokenObtainPairView
# from  base.base_permissions import TokenAccessPermission
# class CustomTokenObtainView(APIView):
#     permission_classes = (AllowAny,)
#     def post(self, request):
#         user = AnonymousUser()
#         token, created = Token.objects.get_or_create(user=user)
#         return JsonResponse({'token': token.key}, status=status.HTTP_200_OK)
    
# class CustomTokenObtainView(CustomAPIView):
#     authentication_classes = []  # No authentication required for this endpoint
#     permission_classes = (AllowAny,)
#     def post(self, request, *args, **kwargs):
#         response = super().post(request, *args, **kwargs)
#         return JsonResponse({'token': response.data['access']}, status=status.HTTP_200_OK)
    
# class CustomTokenObtainView(APIView):
#     permission_classes = (AllowAny,)
#     authentication_classes = []
#     def post(self, request):
#         token = RefreshToken.for_user(AnonymousUser())  # Create a token without a user
#         return JsonResponse({'token': str(token.access_token)}, status=status.HTTP_200_OK)


class OnlineUserList(CustomAPIView, BaseListView):
    paginate_by = 20
    permission_classes = (AllowAny,)
    def get(self, request):
        #checking if user is online and has valid access token to filter out the online users
        qs = CustomUser.objects.filter(Q(is_online=True) & Q(token_expiry_datetime__gt=timezone.now()))
        context = self.get_context_data(object_list=qs)
        return JsonResponse({
            'results': [
                {'id': str(obj.id), 'email': str(obj.email)}
                for obj in context['object_list']
            ],
            'pagination': {'more': context['page_obj'].has_next()},
        })

def calculate_similarity(user_interests, other_user_interests):
    # Get the number of interests that the two users have in common
    num_common_interests = set(user_interests.keys()).intersection(set(other_user_interests.keys()))
    sum_of_common_interest_scores = sum(
        float(user_interests[interest]) + float(other_user_interests[interest])
        for interest in num_common_interests
    )
    return sum_of_common_interest_scores

def get_suggested_friends(user_id,users):
    for user in users:
        if user["id"] == user_id:
            user_interests = user["interests"]
    similarity_scores = {}
    for other_user in users:
        other_user_interests = other_user["interests"]
        similarity_score = calculate_similarity(user_interests, other_user_interests)
        similarity_scores[similarity_score] = other_user
    suggested_friends = sorted(
        similarity_scores.items(), key=lambda x: x[0], reverse=True
    )[:5]
    return [data[1] for data in suggested_friends]

class RecommendFriendsView(CustomAPIView):
    permission_classes = (AllowAny,)
    def get(self, request, user_id=None):
        with open('users.json', 'r') as file:
            data = json.load(file)
        users = data['users']
        top_suggested_friends = get_suggested_friends(user_id, users)
        return JsonResponse({'suggested_friends': top_suggested_friends})