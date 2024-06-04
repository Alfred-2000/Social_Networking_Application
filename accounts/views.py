import logging, uuid, pytz
from datetime import datetime, timedelta
from django.db.models import Q
from rest_framework.views import APIView
from rest_framework.generics import ListCreateAPIView
from rest_framework.response import Response
from rest_framework.status import (
    HTTP_401_UNAUTHORIZED,
    HTTP_200_OK,
    HTTP_201_CREATED,
    HTTP_404_NOT_FOUND,
    HTTP_400_BAD_REQUEST,
)
from accounts.models import (
    Users,
    FollowRequest
)
from social_networking.constants import (
    USER_DOSENT_EXISTS,
    USER_REGISTERED_SUCCESSFULLY,
    USER_LOGGED_IN_SUCCESSFULLY,
    INVALID_CREDENTIALS,
    USER_DELETED_SUCCESSFULLY,
    ENCODE,
    DECODE,
    ACCOUNT_RETRIEVED_SUCCESSFULLY,
    USER_UPDATED_SUCCESSFULLY,
    SUCCESS,
    LIMIT_EXCEEDED,
)
from social_networking.settings import (
    TIME_ZONE,
)
from accounts.serializers import (
    UserSerializer,
    FollowRequestSerializer
)
from accounts.utils import (
    get_current_timestamp_of_timezone,
    hash_given_password,
    encode_decode_jwt_token,
)
from django.shortcuts import get_object_or_404

class LoginView(APIView):
    def post(self, request):
        """
        This method is used to login/sigin account
        """
        try:
            userExist = Users.objects.filter(Q(username=request.data['username'])|Q(email=request.data['username']))

            if userExist.exists():
                user_object = userExist.get()
            else:
                return Response({"status": HTTP_404_NOT_FOUND, "message": USER_DOSENT_EXISTS, "data": []})

            user_details = UserSerializer(user_object, context={"request": request}).data
            request_password = hash_given_password(request.data["password"])

            if request_password == user_details.get('password'):
                admin_token_details = {
                    'id' : user_details.get('user_id'),
                    'username': request.data['username'],
                    'email': user_details.get('email'),
                    'is_superuser': user_details['is_superuser']
                }
                access_token = encode_decode_jwt_token(admin_token_details, convertion_type=ENCODE)
                response = {"status": HTTP_200_OK, "message": USER_LOGGED_IN_SUCCESSFULLY, "data": []}
                logging.info(response)
                return Response(response, headers = {"Authorization": access_token})
            else:
                response = {"status": HTTP_401_UNAUTHORIZED, "error": INVALID_CREDENTIALS, "data": None}
                logging.info(response)
                return Response(response)
        except Exception as error:
            response = {"status": HTTP_400_BAD_REQUEST, "error": error, "data": None}
            logging.info(response)
            return Response(response)
        
class CreateUser(ListCreateAPIView):
    def post(self, request):
        """
        This method is used to register/signup account
        """
        try:
            current_time = get_current_timestamp_of_timezone(TIME_ZONE)
            request.data.update({
                'password': hash_given_password(request.data['password']),
                'created_at': current_time,
                'user_id': uuid.uuid4()
            })
            account_serializer = UserSerializer(data = request.data, context = {'request': request})
            if account_serializer.is_valid():
                account_serializer.save()
                serializer_data = account_serializer.data
                serializer_data['is_superuser'] = str(serializer_data['is_superuser'])
                serializer_data = {k:v for k, v in serializer_data.items() if v != None}
                response = {"status": HTTP_201_CREATED, "message": USER_REGISTERED_SUCCESSFULLY, "data": account_serializer.data}
                logging.info(response)
                return Response(response)
            else:
                response = {"status": HTTP_400_BAD_REQUEST, "error": account_serializer.errors, "data": None}
                logging.info(response)
                return Response(response)

        except Exception as error:
            response = {"status": HTTP_400_BAD_REQUEST, "error": error, "data": None}
            logging.info(response)
            return Response(response)

class ListUsers(ListCreateAPIView):
    queryset = Users.objects.filter(is_superuser=False).all().order_by('-created_at')

    def get(self, request):
        """
        This method is used to get list of all profiles
        """
        try:
            token = request.META.get('HTTP_AUTHORIZATION', None)
            user_name = encode_decode_jwt_token(token, convertion_type=DECODE)['username']
            if self.request.GET.get("search", None):
                search_key = self.request.GET.get("search")
                queryset = self.queryset.filter(Q(username__icontains=search_key) | Q(email=search_key))
            else:
                queryset  = self.queryset
            page = self.paginate_queryset(queryset.exclude(username=user_name))
            if page is not None:
                serializer = UserSerializer(page, many=True, context = {'request': request},
                                    remove_fields=['password', 'email', 'phone_code', 'phone_number', 'is_active',
                                                'is_superuser', 'created_at', 'updated_at', 'timezone'])
                result = self.get_paginated_response(serializer.data)
                return result
        except Exception as error:
            response = {"status": HTTP_400_BAD_REQUEST, "error": error, "data": None}
            logging.info(response)
            return Response(response)
    
class RetrieveUpdateDeleteUser(ListCreateAPIView):
    def get(self, request, **kwargs):
        """
        This method is used to retrieve my account details
        """
        try:
            token = request.META.get('HTTP_AUTHORIZATION', None)
            token_user_id = encode_decode_jwt_token(token, convertion_type=DECODE)['id']
            user_id = str(kwargs['user_id'])
            if token_user_id != user_id:
                response = {"status": HTTP_400_BAD_REQUEST, "data": None}
                logging.info(response)
                return Response(response)
            
            user_query = Users.objects.filter(user_id= user_id)
            user_object = user_query.get()
            user_data = UserSerializer(user_object, context={'request': request}).data
            response = {"status": HTTP_200_OK, "message": ACCOUNT_RETRIEVED_SUCCESSFULLY, "data": user_data}
            logging.info(response)
            return Response(response)
        except Exception as error:
            response = {"status": HTTP_400_BAD_REQUEST, "error": error, "data": None}
            logging.info(response)
            return Response(response)

    def patch(self, request, **kwargs):
        """
        This method is used to update profile(account) settings
        """
        try:
            token = request.META.get('HTTP_AUTHORIZATION', None)
            token_user_id = encode_decode_jwt_token(token, convertion_type=DECODE)['id']
            user_id = str(kwargs['user_id'])
            if token_user_id != user_id:
                response = {"status": HTTP_400_BAD_REQUEST, "data": None}
                logging.info(response)
                return Response(response)

            user_query = Users.objects.filter(user_id = user_id)
            current_time = get_current_timestamp_of_timezone(TIME_ZONE)
            request.data['updated_at'] = current_time
            user_object = user_query.get()
            serializer = UserSerializer(user_object, data=request.data, partial=True, context={'request': request})
            if serializer.is_valid():
                serializer.save()
                response = {"status": HTTP_200_OK, "message": USER_UPDATED_SUCCESSFULLY, "data": serializer.data}
            else:
                response = {"status": HTTP_400_BAD_REQUEST, "error": serializer.errors, "data": None}

            logging.info(response)
            return Response(response)

        except Exception as error:
            response = {"status": HTTP_400_BAD_REQUEST, "error": error, "data": None}
            logging.info(response)
            return Response(response)

    def put(self, request, **kwargs):
        """
        This method is used to delete account
        """
        try:
            token = request.META.get('HTTP_AUTHORIZATION', None)
            token_user_id = encode_decode_jwt_token(token, convertion_type=DECODE)['id']
            user_id = str(kwargs['user_id'])
            if token_user_id != user_id:
                response = {"status": HTTP_400_BAD_REQUEST, "data": None}
                logging.info(response)
                return Response(response)
            
            user_query = Users.objects.filter(user_id=user_id)
            user_object = user_query.get()
            user_object.delete()
            response = {"status": HTTP_200_OK, "message": USER_DELETED_SUCCESSFULLY, "data": None}
            logging.info(response)
            return Response(response)
        except Exception as error:
            response = {"status": HTTP_400_BAD_REQUEST, "error": error, "data": None}
            logging.info(response)
            return Response(response)
        
class FollowUser(ListCreateAPIView):
    def post(self, request, **kwargs):
        """
        This method is used to send friend request
        """
        try:
            token = request.META.get('HTTP_AUTHORIZATION', None)
            from_user_id = encode_decode_jwt_token(token, convertion_type=DECODE)['id']
            one_minute_ago = int((datetime.now() - timedelta(minutes=1)).timestamp())
            user_count = FollowRequest.objects.filter(from_user=from_user_id, created_at__gte=one_minute_ago).order_by('-created_at').count()
            if user_count >=3:
                response = {"status": HTTP_200_OK, "message": LIMIT_EXCEEDED}
                logging.info(response)
                return Response(response)

            request.data.update({
                'from_user': from_user_id,
                'to_user': request.data['user_id']
            })
            serializer = FollowRequestSerializer(data = request.data, context = {'request': request})
            if serializer.is_valid():
                serializer.save()
                response = {"status": HTTP_200_OK, "message": SUCCESS}
            else:
                response = {"status": HTTP_400_BAD_REQUEST, "error": serializer.errors, "data": None}
            logging.info(response)
            return Response(response)
        except Exception as error:
            response = {"status": HTTP_400_BAD_REQUEST, "error": error, "data": None}
            logging.info(response)
            return Response(response)
        
    def patch(self, request, **kwargs):
        """
        This method is used to accept/reject friend requests
        """
        try:
            token = request.META.get('HTTP_AUTHORIZATION', None)
            user_id = encode_decode_jwt_token(token, convertion_type=DECODE)['id']
            try:
                FollowRequest.objects.filter(from_user=request.data['user_id'], to_user=user_id).update(accepted=request.data['accepted'])
                response = {"status": HTTP_200_OK, "message": SUCCESS}
            except Exception as er:
                response = {"status": HTTP_400_BAD_REQUEST, "error": er, "data": None}
            logging.info(response)
            return Response(response)
        except Exception as error:
            response = {"status": HTTP_400_BAD_REQUEST, "error": error, "data": None}
            logging.info(response)
            return Response(response)

class ListMyConnections(ListCreateAPIView):
    queryset = Users.objects.filter(is_superuser=False).all().order_by('-created_at')

    def get(self, request):
        """
        This method is used to get list of my friends and received friend requests
        """
        try:
            connection_type = self.request.GET.get('type', None)
            token = request.META.get('HTTP_AUTHORIZATION', None)
            token_user_id = encode_decode_jwt_token(token, convertion_type=DECODE)['id']
            if connection_type == 'friend':
                connection_query = FollowRequest.objects.filter(from_user=token_user_id, accepted=True).values_list('to_user', flat=True)
            else:
                connection_query = FollowRequest.objects.filter(to_user=token_user_id, accepted=False).values_list('from_user', flat=True)
            friends_id = [str(id) for id in connection_query]
            page = self.paginate_queryset(self.queryset.filter(user_id__in= friends_id))
            if page is not None:
                serializer = UserSerializer(page, many=True, context = {'request': request},
                                    remove_fields=['password', 'email', 'phone_code', 'phone_number', 'is_active',
                                                'is_superuser', 'created_at', 'updated_at', 'timezone'])
                result = self.get_paginated_response(serializer.data)
                return result
        except Exception as error:
            response = {"status": HTTP_400_BAD_REQUEST, "error": error, "data": None}
            logging.info(response)
            return Response(response)
        
class ListUserConnections(ListCreateAPIView):
    queryset = Users.objects.filter(is_superuser=False).all().order_by('-created_at')

    def get(self, request, **kwargs):
        """
        This method is used to get list of particular profile friends
        """
        try:
            user_id = str(kwargs['user_id'])
            connection_query = FollowRequest.objects.filter(to_user=user_id).values_list('from_user', flat=True)
            friends_id = [str(id) for id in connection_query]
            page = self.paginate_queryset(self.queryset.filter(user_id__in= friends_id))
            if page is not None:
                serializer = UserSerializer(page, many=True, context = {'request': request},
                                    remove_fields=['password', 'email', 'phone_code', 'phone_number', 'is_active',
                                                'is_superuser', 'created_at', 'updated_at', 'timezone'])
                result = self.get_paginated_response(serializer.data)
                return result
        except Exception as error:
            response = {"status": HTTP_400_BAD_REQUEST, "error": error, "data": None}
            logging.info(response)
            return Response(response)