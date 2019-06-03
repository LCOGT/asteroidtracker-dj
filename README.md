# Asteroid Tracker

An educational application to allow the general public to make requests using
the [Las Cumbres Observatory](https://lco.global/) Global Telescope Network to
make requests to observe designated asteroids.

This project was originally created for [Asteroid Day 2016](http://asteroidday.org).

The app is visible at [Asteroid Tracker](https://asteroidtracker.lco.global/).

## Build

This project is built automatically by the [LCO Jenkins Server](http://jenkins.lco.gtn/).
Please see the [Jenkinsfile](Jenkinsfile) for more details.

## Production Deployment

This project is deployed on the LCO Kubernetes Cluster. Please refer to the
[LCO Helm Charts Repository](https://github.com/LCOGT/helm-charts) for further
details.

Only deploy tagged releases.

## Version 1.9
- Combine old and new timelapses and upload the combined versions

## Versions 1.8
- Extra compatibility with Django 2.1
- Check JSON in request status
