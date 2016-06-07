from django.shortcuts import render
from django.conf import settings
from django.core.urlresolvers import reverse_lazy
from django.views.generic.detail import DetailView
from django.views.generic import FormView
from django import forms
from django.http import Http404

from observe.models import Asteroid


def home(request):
    asteroids = Asteroid.objects.all()
    return render(request, 'observe/home.html', {'asteroids':asteroids})

class EmailForm(forms.Form):
    user_name = forms.CharField()

class AsteroidView(DetailView):
    """
    Schedule observations on LCOGT given a full set of observing parameters
    """
    model = Asteroid
    template_name = 'observe/asteroid.html'

class LookUpBodyMixin(object):
    '''
    A Mixin for finding a Body from a pk and if it exists, return the Body instance.
    '''
    def dispatch(self, request, *args, **kwargs):
        try:
            body = Asteroid.objects.get(pk=kwargs['pk'])
            self.body = body
            print(body)
            return super(LookUpBodyMixin, self).dispatch(request, *args, **kwargs)
        except Asteroid.DoesNotExist:
            raise Http404("Body does not exist")

class AsteroidSchedule(FormView):
    success_url = reverse_lazy('home')
    form_class = EmailForm

    def post(self, request, *args, **kwargs):
        try:
            body = Asteroid.objects.get(pk=kwargs['pk'])
            self.body = body
            print(body)
            return super(AsteroidSchedule, self).post(request, *args, **kwargs)
        except Asteroid.DoesNotExist:
            raise Http404("Body does not exist")

    def form_valid(self, form):
        print(form)

        # resp_status, resp_msg = process_observation_request(params=obs_params)
        # if not ser.is_valid(raise_exception=True):
        #     return Response(ser.errors, status=status.HTTP_400_BAD_REQUEST)
        # else:
        #     cookie_id=request.session.get('odin.sessionid', False)
        #     if not cookie_id:
        #         return Response("Not authenticated with ODIN.", status=status.HTTP_400_BAD_REQUEST)
        #     proposal = request.session.get('proposal_code', False)
        #     if not proposal:
        #         return Response("No proposals have been registered.", status=status.HTTP_400_BAD_REQUEST)
        #     resp = ser.save(cookie_id=cookie_id, proposal=proposal)
        #     return resp
        return super(AsteroidSchedule, self).form_valid(form)
