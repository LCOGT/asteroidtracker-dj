import requests
import logging
import json
import os
import subprocess
import glob
from datetime import datetime
from django.conf import settings
from django.template import loader, Context

from observe.models import Asteroid
from observe.schedule import get_headers

logger = logging.getLogger('asteroid')

def check_request_api(tracking_num, headers=None):
    '''
    tracking_num: Finds all frames corresponding to this tracking number for UserRequest
    '''
    # Make an authenticated request with our headers
    url = 'https://lcogt.net/observe/api/user_requests/%s/' % tracking_num
    response = requests.get(url, headers=headers)
    frames = []
    if response.status_code == 200:
        # Only proceed if there is a successful response
        response = response.json()
        logger.debug("Checking status of %s requests" % len(response['requests']))
    return response

def set_update_time(date_obs, last_update):
    date_obs, _, us = date_obs.partition(".")
    tmp_date = datetime.strptime(date_obs, "%Y-%m-%dT%H:%M:%S")
    if tmp_date > last_update:
        last_update = tmp_date
    return last_update, tmp_date

def find_frames_object(asteroid):
    '''
    user_reqs: Full User Request dict, or list of dictionaries, containing individual observation requests
    header: provide auth token from the request API so we don't need to get it twice
    '''
    frames = []
    frame_urls = []
    last_update = asteroid.last_update.strftime("%Y-%m-%d %H:%M")
    archive_headers = get_headers(url = 'https://archive-api.lcogt.net/api-token-auth/')
    url = 'http://archive-api.lcogt.net/frames/?RLEVEL=0&start={}&OBJECT={}'.format(last_update, asteroid.text_name())
    response = requests.get(url, headers=archive_headers).json()
    frames = response['results']
    if not response:
        # No frames for this object since last update
        return None
    for frame in frames:
        last_update, date_obs = set_update_time(frame['DATE_OBS'], asteroid.last_update)
        thumbnail_url = "https://thumbnails.lcogt.net/{}/?width=1000&height=1000&label={}".format(frame['id'], date_obs.strftime("%d %b %Y %H:%M"))
        try:
            resp = requests.get(thumbnail_url, headers=archive_headers)
            frame_urls.append({'id':str(frame['id']), 'url':resp.json()['url'],'date_obs':date_obs})
        except ValueError:
            logger.debug("Failed to get thumbnail URL for %s - %s" % (frame_id, resp.status_code))
    logger.debug("Total frames=%s" % (len(frames)))
    return frame_urls, last_update

def find_frames(user_reqs, headers=None):
    '''
    user_reqs: Full User Request dict, or list of dictionaries, containing individual observation requests
    header: provide auth token from the request API so we don't need to get it twice
    '''
    frames = []
    frame_urls = []
    logger.debug("User request: %s" % user_reqs)
    for req in user_reqs:
        url = 'http://archive-api.lcogt.net/frames/?RLEVEL=0&REQNUM={}'.format(req)'
        frames += requests.get(url, headers=headers).json()
    logger.debug('Frames %s' % len(frames))
    return frames

def get_thumbnails(frames):
    for frame_id in frames:
        thumbnail_url = "https://thumbnails.lcogt.net/%s/?width=1000&height=1000" % frame_id['id']
        try:
            resp = requests.get(thumbnail_url, headers=archive_headers)
            frame_urls.append({'id':str(frame_id), 'url':resp.json()['url']})
        except ValueError:
            logger.debug("Failed to get thumbnail URL for %s - %s" % (frame_id, resp.status_code))
    logger.debug("Total frames=%s calibrated=%s" % (len(frames), len(frame_urls)))
    return frame_urls

def download_frames(asteroid_name, frames, download_dir):
    for frame in frames:
        frame_date = frame['date_obs'].strftime("%Y%m%d%H%M%S")
        file_name = '%s_%s.jpg' % (asteroid_name, frame_date)
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
        video_options = "ffmpeg -framerate 10 -pattern_type glob -i '{}' -s 696x520 -vcodec libx264 -pix_fmt yuv420p {} -y".format(path, outfile)
        subprocess.call(video_options, shell=True)
    return len(files)

def email_user(observation_list):
    email_list = []
    for observation in observation_list:
        data = {'observation':observation }
        c = Context(data)
        t = loader.get_template('observe/notify_email.txt')
        text_body = t.render(c)

        email_params = ('Asteroid Day: Update on your asteroid', text_body, 'portal@lcogt.net', [user.email])
        email_list.append(email_params)
    send_mass_mail(tuple(email_list))
    return
