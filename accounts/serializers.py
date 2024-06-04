from rest_framework.serializers import ModelSerializer
from accounts.models import Users, FollowRequest

class UserSerializer(ModelSerializer):
    def __init__(self, *args, **kwargs):
        remove_fields = kwargs.pop('remove_fields', None)
        super(UserSerializer, self).__init__(*args, **kwargs)
        if remove_fields:
            for field_name in remove_fields:
                self.fields.pop(field_name)

    class Meta:
        model = Users
        fields = '__all__'
    
    def to_representation(self, instance):
        representation = super(UserSerializer, self).to_representation(instance)
        if self.context['request'].method == 'GET':
            representation['following'] = FollowRequest.objects.filter(from_user=str(instance.user_id)).count()
            representation['followers'] = FollowRequest.objects.filter(from_user=str(instance.user_id), accepted=True).count()
        return representation

class FollowRequestSerializer(ModelSerializer):

    class Meta:
        model = FollowRequest
        fields = '__all__'