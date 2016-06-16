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

    url = 'https://lcogt.net/observe/auth/accounts/login/'
    r = requests.get(url)
    token = r.cookies['csrftoken']
    r = client.post(url, data={'username':settings.PROPOSAL_USER,'password':settings.PROPOSAL_PASSWD, 'csrfmiddlewaretoken' : token}, cookies={'csrftoken':token})
    url = 'https://lcogt.net/observe/service/request/submit'

    user_request = {'proposal': 'LCOEPO2014B-010', 'request_data':params}
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
    response = requests.post(url, data = auth_data).json()
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
        'name'              : asteroid.text_name(),
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
    # "group_id" : "Asteroid_Day_2016_%s" % asteroid.name
    }
    return json.dumps(user_request)
