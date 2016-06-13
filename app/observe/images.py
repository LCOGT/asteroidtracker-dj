import requests
import logging
import json
import os
import subprocess
import glob
from django.conf import settings

from observe.models import Asteroid, Request
from observe.schedule import get_headers

logger = logging.getLogger('asteroid')

def check_request_api(tracking_num):
    '''
    tracking_num: Finds all frames corresponding to this tracking number for UserRequest
    '''
    headers = get_headers(url = 'https://lcogt.net/observe/api/api-token-auth/')
    # Make an authenticated request with our headers
    url = 'https://lcogt.net/observe/api/user_requests/%s/' % tracking_num
    response = requests.get(url, headers=headers)
    frames = []
    if response.status_code == 200:
        # Only proceed if there is a successful response
        response = response.json()
        logger.debug("Checking status of %s requests" % len(response['requests']))
        frames = find_frames(response['requests'], headers)
    return response, frames

def find_frames(user_reqs, headers=None):
    '''
    user_reqs: Full User Request dict, containing individual observation requests
    header: provide auth token from the request API so we don't need to get it twice
    '''
    frames = []
    frame_urls = []
    for req in user_reqs:
        url = 'https://lcogt.net/observe/api/requests/%s/frames/' % req['request_number']
        frames += requests.get(url, headers=headers).json()
    # Need a new header to access Archive API
    archive_headers = get_headers(url = 'https://archive-api.lcogt.net/api-token-auth/')
    data_products = {'00.fits':'','91.fits':'','11.fits':'', '90.fits':'','10.fits':''}
    for ext, val in data_products.items():
        data_products[ext] = [frame['id'] for frame in frames if ext in frame['filename']]
    # what is data product with the most frames available
    dp = max(data_products, key=data_products.get)
    logger.debug('Most frames available at %s reduction level' % dp)
    for frame_id in data_products[dp]:
        thumbnail_url = "https://thumbnails.lcogt.net/%s/?width=1000&height=1000" % frame_id
        try:
            resp = requests.get(thumbnail_url, headers=archive_headers)
            frame_urls.append({'id':str(frame_id), 'url':resp.json()['url']})
        except ValueError:
            logger.debug("Failed to get thumbnail URL for %s - %s" % (frame_id, resp.status_code))
    logger.debug("Total frames=%s calibrated=%s" % (len(frames), len(frame_urls)))
    return frame_urls

def download_frames(asteroid_name, frames, download_dir):
    for frame in frames:
        file_name = '%s_%s.jpg' % (asteroid_name, frame['id'])
        with open(os.path.join(download_dir, file_name), "wb") as f:
            logger.debug("Downloading %s" % file_name)
            response = requests.get(frame['url'], stream=True)
            logger.debug(frame['url'])
            if response.status_code != 200:
                logger.debug('Failed to download: %s' % response.status_code)
                return False
            total_length = response.headers.get('content-length')

            if total_length is None:
                f.write(response.content)
            else:
                for data in response.iter_content():
                    f.write(data)
        f.close()

    return True

def make_timelapse(asteroid):
    logger.debug('Making timelapse for %s' % asteroid)
    path = "%s%s_*.jpg" % (settings.MEDIA_ROOT,asteroid.text_name())
    files = glob.glob(path)
    if len(files) > 0:
        outfile = '%s%s.mp4' % (settings.MEDIA_ROOT, asteroid.text_name())
        video_options = ['-s', '696x520', '-vcodec', 'libx264', '-pix_fmt', 'yuv420p', outfile, '-y']
        subprocess.call(['ffmpeg', '-framerate', '10', '-pattern_type', 'glob', '-i', '%s' % path] +  video_options)
    return
