from rest_framework import serializers, status
from rest_framework.response import Response
from messierbingo.models import MessierObject, Proposal, Telescope, APERTURES
from game.schedule import process_observation_request, request_format
from django.conf import settings

class ScopeSerializer(serializers.ModelSerializer):
    class Meta:
        model = Telescope
        fields = ('name','aperture')

class RequestSerializer(serializers.Serializer):
    """
    This serializer POSTing parameters to the scheduler the api.
    """
    user_name = serializers.CharField()

    def save(self, *args, **kwargs):
        obs_params = request_format(kwargs['asteroid_id'])
        resp_status, resp_msg = process_observation_request(params=obs_params)
        if resp_status:
            return Response('Success', status=status.HTTP_201_CREATED)
        else:
            return Response(resp_msg, status=status.HTTP_400_BAD_REQUEST)
