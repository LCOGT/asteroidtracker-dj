from django.contrib.sessions.backends.db import SessionStore
import requests
import logging
import json
from django.conf import settings

from observe.models import Asteroid


logger = logging.getLogger('asteroid')

def process_observation_request(user_request):
    '''
    Send the observation parameters and the authentication cookie to the Scheduler API
    '''
    client = requests.session()
    json_user_request = json.dumps(user_request)
    params = {
            'proposal_id'   : 'LCOEPO2014B-010',
            'user_id'       : settings.PROPOSAL_USER,
            'password'      : settings.PROPOSAL_PASSWD,
           'request_data' : json_user_request}

    url = 'https://lcogt.net/observe/service/request/submit'
    r = client.post(url, data=params)
    if r.status_code == 200:
        return True, False
    else:
        logger.error(r.content)
        return False, r.content


def format_request(asteroid_id):

    try:
        asteroid = Asteroid.objects.get(id=asteroid_id)
    except:
        raise

    # this selects any telescope on the 1 meter network
    location = {
        'telescope_class' : asteroid.aperture,
        }

    molecule = {
      # Required fields
    'exposure_time'   : asteroid.exposure,  # Exposure time, in secs
    'exposure_count'  : 1,  # The number of consecutive exposures
    'filter'          : asteroid.filter_name,  # The generic filter name
    # Optional fields. Defaults are as below.
    # fill_window should be defined as True on a maximum of one molecule per request, or you should receive an error when scheduling
    'fill_window'     : False, # set to True to cause this molecule to fill its window (or all windows of a cadence) with exposures, calculating exposure_count for you
    'type'            : 'EXPOSE',  # The type of the molecule
    'ag_name'         : '',  # '' to let it resolve; same as instrument_name for self-guiding
    'ag_mode'         : 'Optional',
    'instrument_name' : asteroid.instrument,  # This resolves to the main science camera on the scheduled resource
    'bin_x'           : asteroid.binning,  # Your binning choice. Right now these need to be the same.
    'bin_y'           : asteroid.binning,
    'defocus'         : 0.0  # Mechanism movement of M2, or how much focal plane has moved (mm)
    }

    # define the target
    target = {
        'name'              : asteroid.name,
        'type'              : asteroid.type,
        'orbinc'            : asteroid.orbinc,
        'argofperih'        : asteroid.argofperih,
        'longascnode'       : asteroid.longascnode,
        'epochofel'         : asteroid.epochofel,
        'eccentricity'       : asteroid.eccentricity,
        'meananom'           : asteroid.meananom,
        'meandist'           : asteroid.meandist,
    }

    # this is the actual window
    window = {
          'start' : str(asteroid.start)
          'end' : str(asteroid.end)
    }

    request = {
    "constraints" : {'max_airmass' : 2.0},
    "location" : location,
    "molecules" : [molecule],
    "observation_note" : "",
    "observation_type" : "NORMAL",
    "target" : target,
    "type" : "request",
    "windows" : [window],
    }

    user_request = {
    "operator" : "single",
    "requests" : [request],
    "type" : "compound_request"
    }
    return user_request
