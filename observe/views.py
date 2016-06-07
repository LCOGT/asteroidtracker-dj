from django.shortcuts import render
from django.conf import settings
from django.core.urlresolvers import reverse
from django.views.generic.edit import UpdateView

from observe.models import Asteroid


def home(request):
    asteroids = Asteroid.objects.all()
    return render(request, 'observe/home.html', {'asteroids':asteroids})

class AsteroidView(UpdateView):
    """
    Schedule observations on LCOGT given a full set of observing parameters
    """
    model = Asteroid
    template_name = 'observe/asteroid.html'
    fields = ['information','name']

    def post(self, request, format=None):
        resp_status, resp_msg = process_observation_request(params=obs_params)
        if not ser.is_valid(raise_exception=True):
            return Response(ser.errors, status=status.HTTP_400_BAD_REQUEST)
        else:
            cookie_id=request.session.get('odin.sessionid', False)
            if not cookie_id:
                return Response("Not authenticated with ODIN.", status=status.HTTP_400_BAD_REQUEST)
            proposal = request.session.get('proposal_code', False)
            if not proposal:
                return Response("No proposals have been registered.", status=status.HTTP_400_BAD_REQUEST)
            resp = ser.save(cookie_id=cookie_id, proposal=proposal)
            return resp
