import requests
import logging
import json
from django.conf import settings

from observe.models import Asteroid, Request

logger = logging.getLogger('asteroid')

def find_frames(user_reqs, headers=None):
    frames = []
    frame_urls = []
    for req in user_reqs:
        frames_url = 'https://lcogt.net/observe/api/requests/%s/frames/' % req['request_number']
        frames += requests.get(frames_url, headers=headers).json()
    for frame in frames:
        if '91.fits' in f['filename']:
            thumnail_url = "https://thumbnails.lcogt.net/%s/?width=1000&height=1000" % f['id']
            resp = requests.get(thumbnail_url, headers=headers).json()
    return frame_urls
def download_images(frames):

    return

def make_timelapse():
    return
