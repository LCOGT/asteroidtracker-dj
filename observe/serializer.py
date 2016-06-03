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
    asteroid_name = serializers.CharField()
    user_name = serializers.CharField()

    def save(self, *args, **kwargs):
        params = self.data
        obs_params = request_format(params['asteroid_name'])
        resp_status, resp_msg = process_observation_request(params=obs_params, cookie_id=kwargs['cookie_id'])
        if resp_status:
            return Response('Success', status=status.HTTP_201_CREATED)
        else:
            return Response(resp_msg, status=status.HTTP_400_BAD_REQUEST)
