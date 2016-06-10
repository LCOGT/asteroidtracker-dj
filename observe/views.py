from django.shortcuts import render
from django.conf import settings
from django.core.urlresolvers import reverse_lazy
from django.views.generic.detail import DetailView
from django.views.generic import FormView
from django import forms
from django.http import Http404
from datetime import datetime

from observe.schedule import format_request, submit_scheduler_api, check_request_api

from observe.models import Asteroid, Request
import logging

logger = logging.getLogger('asteroid')
state_options = {'PENDING' : 'P', 'COMPLETED' :'C', 'CANCELED':'N', 'FAILED':'F', 'UNSCHEDULABLE':'F'}


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
        resp = process_form(self.body, form.cleaned_data)
        if resp:
            self.success_url = reverse_lazy('asteroid_detail', kwargs={'pk':self.body.id})
            return render(self.request, 'observe/asteroid.html', {'asteroid':self.body, 'user_request':resp})
        else:
            return super(AsteroidSchedule, self).form_valid(form)

def update_status(req):
    status, frames = check_request_api(req.track_num)
    logger.debug(status)
    req.status = state_options[status['state']]
    req.update = datetime.utcnow()
    req.save()
    return frames


def send_request(asteroid, form):
    obs_params = format_request(asteroid)
    resp_status, resp_msg = submit_scheduler_api(obs_params)
    #resp_status, resp_msg = (True, '999')
    if resp_status:
        req_params = {
            'track_num' : resp_msg,
            'status'    : 'P',
            'email'     : form['user_name'],
            'asteroid'  : asteroid,
        }
        r = Request(**req_params)
        r.save()
        logger.debug('Saved request %s' % r)
    else:
        logger.error('Request not scheduled: %s' % resp_msg)
    return None

def process_form(asteroid, form):
    try:
        req = Request.objects.get(asteroid=asteroid, email=form['user_name'])
    except Request.DoesNotExist:
        return send_request(asteroid, form)
    frames = update_status(req)
    return {'frames' :frames, 'status':req}
