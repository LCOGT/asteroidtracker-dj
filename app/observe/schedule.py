import requests
import logging
import json
from django.conf import settings

from observe.models import Asteroid

logger = logging.getLogger('asteroid')

def submit_scheduler_api(params):
    '''
    Send the observation parameters and the authentication cookie to the Scheduler API
    '''
    client = requests.session()

    url = 'https://lco.global/observe/auth/accounts/login/'
    r = requests.get(url)
    token = r.cookies['csrftoken']
    r = client.post(url, data={'username':settings.PROPOSAL_USER,'password':settings.PROPOSAL_PASSWD, 'csrfmiddlewaretoken' : token}, cookies={'csrftoken':token})
    url = 'https://lco.global/observe/service/request/submit'

    user_request = {'proposal': settings.PROPOSAL_CODE, 'request_data':json.dumps(params)}
    r = client.post(url, data=user_request, cookies=client.cookies)
    client.close()
    if r.status_code == 200:
        tracking_num = r.json()['id']
        logger.debug('Request submitted - %s' % tracking_num)
        return True, tracking_num
    else:
        logger.error(r.content)
        return False, r.content

def get_headers(url):
    auth_data = {'username':settings.PROPOSAL_USER, 'password':settings.PROPOSAL_PASSWD}
    response = requests.post(url, data = auth_data)
    if response.status_code == 200:
        response = response.json()
    else:
        return False
    token = response.get('token')
    # Store the Authorization header
    headers = {'Authorization': 'Token {}'.format(token)}
    return headers

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
    'ag_mode'         : 'Optional',
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
        'epochofel'         : asteroid.epochofel_mjd(),
        'eccentricity'      : asteroid.eccentricity,
        'meananom'          : asteroid.meananom,
        'meandist'          : asteroid.meandist,
    }

    # this is the actual window
    window = {
          'start' : str(asteroid.start),
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
    "type" : "compound_request",
    "ipp_value" : 1.0,
    # "group_id" : "Asteroid_Day_2016_%s" % asteroid.name
    }
    return user_request
