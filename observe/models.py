from __future__ import unicode_literals

from django.db import models
from datetime import datetime

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

ELEMENTS_TYPES = (('MPC_MINOR_PLANET','MPC Minor Planet'),('MPC_COMET','MPC Comet'))

class Asteroid(models.Model):
    name                = models.CharField('Designation',max_length=15, blank=True, null=True)
    source_type         = models.CharField('Type of object',max_length=1,choices=OBJECT_TYPES,blank=True, null=True)
    elements_type       = models.CharField('Elements type', max_length=16, choices=ELEMENTS_TYPES,blank=True, null=True)
    active              = models.BooleanField('Actively following?', default=False)
    epochofel           = models.DateTimeField('Epoch of elements',blank=True, null=True)
    orbinc              = models.FloatField('Orbital inclination in deg',blank=True, null=True)
    longascnode         = models.FloatField('Longitude of Ascending Node (deg)',blank=True, null=True)
    argofperih          = models.FloatField('Arg of perihelion (deg)',blank=True, null=True)
    eccentricity        = models.FloatField('Eccentricity',blank=True, null=True)
    meandist            = models.FloatField('Mean distance (AU)', blank=True, null=True, help_text='for asteroids')
    meananom            = models.FloatField('Mean Anomaly (deg)', blank=True, null=True, help_text='for asteroids')
    perihdist           = models.FloatField('Perihelion distance (AU)', blank=True, null=True, help_text='for comets')
    epochofperih        = models.DateTimeField('Epoch of perihelion', blank=True, null=True, help_text='for comets')
    arc_length          = models.FloatField('Length of observed arc (days)', blank=True, null=True)
    exposure            = models.IntegerField(default=0)
    filter_name         = models.CharField(max_length=10)
    exposure_count      = models.IntegerField(default=1)
    start               = models.DateTimeField(default=datetime.utcnow())
    end                 = models.DateTimeField(default=datetime.utcnow())
    instrument          = models.CharField(max_length=30)
    aperture            = models.CharField(max_length=3)
    binning             = models.IntegerField(default=2)
    information         = models.TextField(blank=True, null=True)
    teaser              = models.CharField(max_length=120)
    image               = models.TextField(default="no-image.jpg")
    timelapse_url       = models.URLField()

    def __unicode__(self):
        return self.name


class Request(models.Model):
    track_num           = models.CharField(max_length=10)
    status              = models.CharField(max_length=1)
    update_time         = models.DateTimeField(blank=True, null=True)
    email               = models.CharField(max_length=150)
    twitter             = models.CharField(max_length=15)
    asteroids           = models.ForeignKey(Asteroid)
