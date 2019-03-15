from datetime import datetime
from django.conf import settings
from django.core.mail import send_mass_mail
from django.template import loader, Context
import ffmpeg
import glob
import json
import logging
import os
import requests
import subprocess

from observe.models import Asteroid
from observe.schedule import get_headers

logger = logging.getLogger('asteroid')

def check_request_api(tracking_num):
    '''
    tracking_num: Finds all frames corresponding to this tracking number for UserRequest
    '''
    # Make an authenticated request with our headers
    headers = get_headers('O')
    url = '{}user_requests/{}/'.format(settings.OBSERVE_URL,tracking_num)
    response = requests.get(url, headers=headers)
    frames = []
    if response.status_code == 200:
        # Only proceed if there is a successful response
        response = response.json()
        logger.debug("Checking status of %s requests" % len(response.get('requests','')))
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
    archive_headers = get_headers('A')
    url = '{}frames/?RLEVEL=91&start={}&OBJECT={}'.format(settings.ARCHIVE_URL, last_update, asteroid.name)
    response = requests.get(url, headers=archive_headers).json()
    frames = response['results']
    logger.debug("Found {} frames".format(len(frames)))
    if not response:
        # No frames for this object since last update
        return None
    for frame in frames:
        logger.debug("Looking for frame {}".format(frame['id']))
        last_update, date_obs = set_update_time(frame['DATE_OBS'], asteroid.last_update)
        thumbnail_url = "{}{}/?width=1000&height=1000&label={}".format(settings.THUMBNAIL_URL, frame['id'], date_obs.strftime("%d %b %Y %H:%M"))
        try:
            resp = requests.get(thumbnail_url, headers=archive_headers)
            frame_urls.append({'id':str(frame['id']), 'url':resp.json()['url'],'date_obs':date_obs})
        except ValueError:
            logger.debug("Failed to get thumbnail URL for %s - %s" % (frame_id, resp.status_code))
    logger.debug("Total frames=%s" % (len(frames)))
    return frame_urls, last_update

def find_frames(user_reqs, last_update):
    '''
    user_reqs: Full User Request dict, or list of dictionaries, containing individual observation requests
    header: provide auth token from the request API so we don't need to get it twice
    '''
    frames = []
    logger.debug("User request: %s" % user_reqs)
    headers = get_headers('A')
    for req in user_reqs:
        url = '{}frames/?RLEVEL=91&REQNUM={}&start={}'.format(settings.ARCHIVE_URL, req, last_update.isoformat())
        print(url)
        resp = requests.get(url, headers=headers).json()
        if resp.get('detail',''):
            logger.error(resp['detail'])
            continue
        if resp['count'] > 0:
            frames += [f['id'] for f in resp['results']]
    logger.debug('Frames %s' % len(frames))
    return frames

def get_thumbnails(frames):
    headers = get_headers(mode='A')
    frame_urls = []
    for frame_id in frames:
        thumbnail_url = "{}{}/?width=1000&height=1000".format(settings.THUMBNAIL_URL, frame_id['id'])
        try:
            resp = requests.get(thumbnail_url, headers=headers)
            frame_urls.append({'id':str(frame_id), 'url':resp.json()['url']})
        except ValueError:
            logger.debug("Failed to get thumbnail URL for %s - %s" % (frame_id, resp.content))
    logger.debug("Total frames=%s calibrated=%s" % (len(frames), len(frame_urls)))
    return frame_urls

def download_frames(asteroid_name, frames, download_dir):
    for frame in frames:
        frame_date = frame['date_obs'].strftime("%Y%m%d%H%M%S")
        file_name = '%s_%s.jpg' % (asteroid_name, frame_date)
        full_filename = os.path.join(download_dir, file_name)

        with open(full_filename, "wb") as f:
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

def make_timelapse(asteroid, file_dir, format="mp4"):
    logger.debug('Making {} timelapse for {}'.format(format, asteroid))
    path = os.path.join(file_dir, "*.jpg")
    files = glob.glob(path)
    asteroid.num_observations += len(files)
    asteroid.save()
    if files:
        if format == 'mp4':
            outfile = '{}.mp4'.format(asteroid.name.replace(" ", "_"))
            outfile = os.path.join(file_dir, outfile)
            video_options = "ffmpeg -framerate 10 -pattern_type glob -i '{}' -vf 'scale=2*iw:-1, crop=iw/2:ih/2' -s 696x520 -vcodec libx264 -f mp4 -pix_fmt yuv420p {} -y".format(path, outfile)
        elif format == 'webm':
            outfile = '{}.webm'.format(asteroid.name.replace(" ", "_"))
            outfile = os.path.join(file_dir, outfile)
            video_options = "ffmpeg -framerate 10 -pattern_type glob -i '{}' -vf 'scale=2*iw:-1, crop=iw/2:ih/2' -s 696x520 -vcodec libvpx-vp9 -f webm {} -y".format(path, outfile)

        try:
            output = subprocess.check_output(
                video_options, stderr=subprocess.STDOUT, shell=True, timeout=30,
                universal_newlines=True)
        except subprocess.CalledProcessError as exc:
            logger.error("Status : FAIL", exc.returncode, exc.output)
        else:
            logger.debug("Output: \n{}\n".format(output))
            return outfile
    return False

# def combine_timelapses(path, outfile):
#     video_options = "ffmpeg -f concat -safe 0 -i <(for f in {}; do echo "file '$PWD/$f'"; done) -c copy {}.mp4 -y".format(path, outfile)
#     proc = subprocess.Popen(video_options)
#     try:
#         outs, errs = proc.communicate(timeout=60)
#         return outfile
#     except TimeoutExpired:
#         proc.kill()
#         outs, errs = proc.communicate()
#     return

def email_users(observation_list):
    email_list = []
    for observation in observation_list:
        data = {'observation':observation }
        c = Context(data)
        t = loader.get_template('observe/notify_email.txt')
        text_body = t.render(c)

        email_params = ('Asteroid Tracker: Update on your asteroid', text_body, settings.DEFAULT_FROM_EMAIL, [observation.email])
        email_list.append(email_params)

    if not settings.EMAIL_ENABLED:
        logger.debug('Email is disabled, skip sending {} email notifications'.format(len(observation_list)))
        return

    send_mass_mail(tuple(email_list))
    logger.debug('Emailed {} people'.format(len(observation_list)))
    return
