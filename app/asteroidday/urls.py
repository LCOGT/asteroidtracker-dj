"""asteroidday URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/1.9/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  url(r'^$', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  url(r'^$', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.conf.urls import url, include
    2. Add a URL to urlpatterns:  url(r'^blog/', include('blog.urls'))
"""
from django.conf.urls import url
from django.contrib import admin
from django.contrib.flatpages import views
from django.conf.urls.static import static
from django.conf import settings

from observe.views import AsteroidView, AsteroidSchedule, ObservationView, home
from observe.models import Asteroid


urlpatterns = [
    url(r'^$', home , name='home'),
    url(r'^about/$', views.flatpage, {'url': '/about/'}, name='about'),
    url(r'^education/$', views.flatpage, {'url': '/education/'}, name='education'),
    url(r'^asteroid/(?P<pk>[0-9]+)/$', AsteroidView.as_view(), name='asteroid_detail'),
    url(r'^asteroid/(?P<pk>[0-9]+)/submit/$', AsteroidSchedule.as_view(), name='asteroid_schedule'),
    url(r'^observation/(?P<pk>[0-9]+)/$', ObservationView.as_view(), name='request_detail'),
    url(r'^admin/', admin.site.urls),
]  + static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
