import logging, pytz, json, uuid
from django.http import HttpRequest
from django.core.management import BaseCommand
from datetime import datetime
from social_networking.constants import debug_user_details
from accounts.models import Users
from accounts.utils import (
    get_current_timestamp_of_timezone,
    hash_given_password
)
from social_networking.settings import (
    TIME_ZONE
)
from accounts.serializers import UserSerializer


class Command(BaseCommand):
    help = "This management command is used for creating debug user"

    def handle(self, *args, **options):
        try:
            user_request = HttpRequest()
            user_request.method = 'POST'
            created_time = get_current_timestamp_of_timezone(TIME_ZONE)            
            try:
                if not Users.objects.filter(username = debug_user_details['username']).exists():
                    debug_user_details.update({
                        'user_id': uuid.uuid4(),
                        'created_at': created_time,
                        'password': hash_given_password(debug_user_details['password'])
                    })
                    debug_user_serializer = UserSerializer(data = debug_user_details, context = {'request' : user_request})
                    if debug_user_serializer.is_valid():
                        debug_user_serializer.save()
                    logging.info("Debug admin {} created successfully !!!".format(debug_user_details['username']))
                else:
                    logging.info("Debug admin {} already exists !!!".format(debug_user_details['username']))
            except Exception as error:
                logging.exception("Exception occured while creating debug admin {} Errors: {}".format(error))

        except Exception as error:
            logging.error(error)

