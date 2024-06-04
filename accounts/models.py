import time
from django.db import models

class Users(models.Model):
    user_id = models.UUIDField(primary_key=True)
    username = models.CharField(max_length=150, unique=True)
    password = models.CharField(max_length=100)
    email = models.CharField(max_length=256, null=True, blank=True, unique=True)
    phone_code = models.CharField(max_length=6, null=True, blank=True)
    phone_number = models.TextField(blank=True, null=True, unique=True)
    is_active = models.BooleanField(default=True)
    is_superuser = models.BooleanField(default=False)
    private_account = models.BooleanField(default=False)
    country = models.CharField(max_length=200)
    timezone = models.CharField(max_length=32, null=True, blank=True)
    created_at = models.BigIntegerField(default=int(time.time()))
    updated_at = models.BigIntegerField(null=True, blank=True)

    def __str__(self):
        return self.username
   
class FollowRequest(models.Model):
    from_user = models.ForeignKey('accounts.Users', on_delete=models.CASCADE, blank=True, null=True, related_name='sent_requests')
    to_user = models.ForeignKey('accounts.Users', on_delete=models.CASCADE, blank=True, null=True, related_name='received_requests')
    accepted = models.BooleanField(default=False)
    created_at = models.BigIntegerField(default=int(time.time()))

    class Meta:
        unique_together = ('from_user', 'to_user')