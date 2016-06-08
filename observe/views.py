from django.shortcuts import render
from django.conf import settings
from django.core.urlresolvers import reverse_lazy
from django.views.generic.detail import DetailView
from django.views.generic import FormView
from django import forms
from django.http import Http404

from observe.schedule import process_observation_request, format_request

from observe.models import Asteroid
import logging

logger = logging.getLogger('asteroid')

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

class AsteroidSchedule(FormView):
    success_url = reverse_lazy('home')
    form_class = EmailForm

    def post(self, request, *args, **kwargs):
        try:
            body = Asteroid.objects.get(pk=kwargs['pk'])
            self.body = body
            return super(AsteroidSchedule, self).post(request, *args, **kwargs)
        except Asteroid.DoesNotExist:
            raise Http404("Asteroid does not exist")

    def form_valid(self, form):
        obs_params = format_request(self.body)
        resp_status, resp_msg = process_observation_request(user_request=obs_params)
        return super(AsteroidSchedule, self).form_valid(form)
