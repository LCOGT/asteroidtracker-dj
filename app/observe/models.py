from __future__ import unicode_literals

from django.db import models
from django.utils import timezone
from datetime import datetime

from astropy.time import Time


OBJECT_TYPES = (
                ('N','NEO'),
                ('A','Asteroid'),
                ('C','Comet'),
                ('K','KBO'),
                ('E','Centaur'),
                ('T','Trojan'),
                ('U','Candidate'),
                ('X','Did not exist'),
                ('W','Was not interesting'),
                ('D','Discovery, non NEO'),
                ('J','Artificial satellite')
            )

STATUS_CHOICES = (
                ('P','Pending'),
                ('C','Completed'),
                ('S','Scheduled'),
                ('N','Canceled'),
                ('F','Failed')
                )

ELEMENTS_TYPES = (('MPC_MINOR_PLANET','MPC Minor Planet'),('MPC_COMET','MPC Comet'))

INSTRUMENTS =  (('1M0-SCICAM-SBIG', '1m'),
                ('2M0-SCICAM-SPECTRAL', '2m'),
                ('0M4-SCICAM-SBIG', '0.4m')
                    )

class Asteroid(models.Model):
    name                = models.CharField('Designation',max_length=15, blank=True, null=True)
    source_type         = models.CharField('Type of object',max_length=1,choices=OBJECT_TYPES,blank=True, null=True)
    elements_type       = models.CharField('Elements type', max_length=16, choices=ELEMENTS_TYPES,blank=True, null=True)
    active              = models.BooleanField('Actively following?', default=False)
    epochofel           = models.FloatField('Epoch of elements',blank=True, null=True)
    orbinc              = models.FloatField('Orbital inclination in deg',blank=True, null=True)
    longascnode         = models.FloatField('Longitude of Ascending Node (deg)',blank=True, null=True)
    argofperih          = models.FloatField('Arg of perihelion (deg)',blank=True, null=True)
    eccentricity        = models.FloatField('Eccentricity',blank=True, null=True)
    meandist            = models.FloatField('Mean distance (AU)', blank=True, null=True, help_text='for asteroids')
    meananom            = models.FloatField('Mean Anomaly (deg)', blank=True, null=True, help_text='for asteroids')
    exposure            = models.IntegerField(default=0)
    filter_name         = models.CharField(max_length=10)
    exposure_count      = models.IntegerField(default=1)
    start               = models.DateTimeField(default=datetime.utcnow)
    end                 = models.DateTimeField(default=datetime.utcnow)
    instrument          = models.CharField(max_length=30, choices=INSTRUMENTS)
    aperture            = models.CharField(max_length=3)
    binning             = models.IntegerField(default=2)
    information         = models.TextField(blank=True, null=True)
    teaser              = models.CharField(max_length=120)
    image_url           = models.URLField(default="https://lco.global/files/astronomy/asteroid/unknown.jpg")
    timelapse_url       = models.URLField(blank=True, null=True)
    num_observations    = models.IntegerField(default=0)
    last_update         = models.DateTimeField(default=timezone.now)

    def epochofel_mjd(self):
        mjd = None
        try:
            t = Time(self.epochofel.isoformat(), format='isot', scale='tt')
            mjd = t.mjd
        except:
            pass
        return mjd

    def epochofperih_mjd(self):
        mjd = None
        try:
            t = Time(self.epochofperih.isoformat(), format='isot', scale='tt')
            mjd = t.mjd
        except:
            pass
        return mjd

    def text_name(self):
        return self.name.replace(" ","_")

    def __unicode__(self):
        return self.name


class Observation(models.Model):
    track_num           = models.CharField(max_length=10)
    status              = models.CharField(max_length=1, choices=STATUS_CHOICES)
    last_update         = models.DateTimeField(default=timezone.now)
    email               = models.CharField(max_length=150, blank=True, null=True)
    asteroid            = models.ForeignKey(Asteroid)
    request_ids         = models.TextField(blank=True, null=True)
    frame_ids           = models.TextField(blank=True, null=True)

    def __unicode__(self):
        return "%s for %s is %s" % (self.track_num, self.email, self.status)
