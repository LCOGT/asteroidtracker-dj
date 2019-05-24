import requests
import logging
import json
from datetime import datetime, timedelta

from django.conf import settings

from observe.models import Asteroid

logger = logging.getLogger(__name__)


def submit_scheduler_api(params):
    '''
    Send the observation parameters and the authentication cookie to the Scheduler API
    '''
    headers = {'Authorization': 'Token {}'.format(settings.PORTAL_TOKEN)}
    url = settings.PORTAL_REQUEST_API
    try:
        r = requests.post(url, json=params, headers=headers, timeout=20.0)
    except requests.exceptions.Timeout:
        msg = "Observing portal API timed out"
        logger.error(msg)
        params['error_msg'] = msg
        return False, msg

    if r.status_code in [200,201]:
        logger.debug('Submitted request {}'.format(r.json()))
        return True, r.json()
    else:
        logger.error("Could not send request: {}".format(r.content))
        return False, r.content

def get_headers(mode='O'):
    if mode == 'A':
        token = settings.ARCHIVE_TOKEN
        headers = {'Authorization': 'Token {}'.format(token)}
    elif mode == 'O':
        token = settings.PORTAL_TOKEN
        headers = {'Authorization': 'Token {}'.format(token)}
    return headers

def calc_end_date(start, semester, interval):
    # We want to avoid semester boundaries but still give enough time to get DATABASES
    obs_window = timedelta(days=interval)
    end = start + obs_window
    if end > semester:
        end = semester - timedelta(seconds=1)
    if end - start < timedelta(days=3):
        # if obs window is < 3 days it won't happen, bump to next semester
        start = semester
        end = start + obs_window
    return start, end


def format_request(asteroid):

    # this selects any telescope on the 1 meter network
    location = {
        'telescope_class' : asteroid.aperture,
        }

    molecule = {
      # Required fields
    'exposure_time'   : asteroid.exposure,  # Exposure time, in secs
    'exposure_count'  : asteroid.exposure_count,  # The number of consecutive exposures
    'filter'          : asteroid.filter_name,  # The generic filter name
    'fill_window'     : False,
    'type'            : 'EXPOSE',
    'ag_mode'         : 'OPTIONAL',
    'instrument_name' : asteroid.instrument,
    }

    # define the target
    target = {
        'name'              : asteroid.name,
        'type'              : 'NON_SIDEREAL',
        'scheme'            : 'MPC_MINOR_PLANET',
        'orbinc'            : asteroid.orbinc,
        'argofperih'        : asteroid.argofperih,
        'longascnode'       : asteroid.longascnode,
        'epochofel'         : asteroid.epochofel,
        'eccentricity'      : asteroid.eccentricity,
        'meananom'          : asteroid.meananom,
        'meandist'          : asteroid.meandist,
    }


    # this is the actual window
    startdate, enddate = calc_end_date(datetime.utcnow(), asteroid.semester_end, asteroid.observe_interval)
    window = {
          'start' : str(startdate),
          'end' : str(enddate)
    }

    request = {
        "constraints" : {'max_airmass' : 1.74},
        "location" : location,
        "molecules" : [molecule],
        "observation_note" : "",
        "target" : target,
        "windows" : [window]
    }

    user_request = {
        "submitter": settings.PROPOSAL_USER,
        "requests": [request],
        "group_id" : "ad{}_{}_{}".format(datetime.utcnow().year, asteroid.text_name(), datetime.utcnow().strftime("%Y%m%d")),
        "observation_type": "NORMAL",
        "operator": "SINGLE",
        "ipp_value": 1.0,
        "proposal": settings.PROPOSAL_CODE
    }
    return user_request
