from django.shortcuts import render, redirect
from django.conf import settings
from django.contrib import messages
from django.core.urlresolvers import reverse_lazy
from django.views.generic.detail import DetailView
from django.views.generic import FormView
from django.core.mail import send_mass_mail
from django import forms
from django.http import Http404
from datetime import datetime
import json

from observe.schedule import format_request, submit_scheduler_api, get_headers
from observe.images import check_request_api, download_frames, find_frames, get_thumbnails
from observe.models import Asteroid, Observation
import logging

logger = logging.getLogger('asteroid')
state_options = {'PENDING' : 'P', 'COMPLETED' :'C', 'CANCELED':'N', 'FAILED':'F', 'UNSCHEDULABLE':'F'}


def home(request):
    asteroids = Asteroid.objects.all()
    return render(request, 'observe/home.html', {'asteroids':asteroids})

class EmailForm(forms.Form):
    user_name = forms.CharField()

class ObservationView(DetailView):
    """
    View observations on LCOGT
    """
    model = Observation
    template_name = 'observe/observation.html'

    def get_context_data(self, **kwargs):
        # Call the base implementation first to get a context
        context = super(ObservationView, self).get_context_data(**kwargs)
        # Add in a QuerySet of all the books
        fids = self.object.frame_ids
        if fids:
            headers = get_headers(url = 'https://archive-api.lcogt.net/api-token-auth/')
            frame_ids = [{'id':f} for f in json.loads(fids)]
            context['frames'] = get_thumbnails(frame_ids, headers)
        return context

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
        try:
            req = Observation.objects.get(asteroid=self.body, email=form.cleaned_data['user_name'])
        except Observation.DoesNotExist:
            resp = send_request(self.body, form)
            messages.add_message(self.request, resp['code'] , resp['msg'])
            return super(AsteroidSchedule, self).form_valid(form)

        messages.info(self.request,"Checking status of your %s observations" % self.body.name)
        return redirect('request_detail', pk=req.id)


def update_status(req):
    if not req.request_ids:
        logger.debug("Finding request IDs for {}".format(req))
        headers = get_headers(url = 'https://lcogt.net/observe/api/api-token-auth/')
        status = check_request_api(req.track_num, headers)
        request_ids = [r['request_number'] for r in status['requests']]
        req.request_ids = json.dumps(request_ids)
        req.save()
    if not req.frame_ids:
        logger.debug("Finding frame IDs for {}".format(req))
        archive_headers = get_headers(url = 'https://archive-api.lcogt.net/api-token-auth/')
        frames = find_frames(json.loads(req.request_ids), archive_headers)
        req.frame_ids = json.dumps(frames)
        if len(frames) == req.asteroid.exposure_count:
            req.status = 'C'
            req.update = datetime.utcnow()
            req.save()
            return True
    return False

def send_request(asteroid, form):
    obs_params = format_request(asteroid)
    resp_status, resp_msg = submit_scheduler_api(obs_params)
    if resp_status:
        req_params = {
            'track_num' : resp_msg,
            'status'    : 'P',
            'email'     : form.cleaned_data['user_name'],
            'asteroid'  : asteroid,
        }
        r = Observation(**req_params)
        r.save()
        msg = "Observations submitted successfully"
        code = messages.SUCCESS
        logger.debug('Saved request %s' % r)
    else:
        msg = 'Observation not scheduled: %s' % resp_msg
        logger.error(resp_msg)
        code = messages.ERROR
    return {'status':None, 'msg': msg,'code':code}
