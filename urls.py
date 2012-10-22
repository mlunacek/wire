from django.conf.urls import patterns, include, url
from django.views.generic import ListView

import wire.views as wire

urlpatterns = patterns('',

   url(r'^$', 'django.views.generic.simple.direct_to_template', {'template': 'home.html'}, name='home'),
   url(r'^documentation/$', 'django.views.generic.simple.direct_to_template', {'template': 'documentation.html'}, name='documentation'),
   url(r'^summary/$', wire.summary_redirect, name='summary'),   
   url(r'^summary/(?P<year>\d{4})-(?P<month>\d{2})-(?P<day>\d{2})/(?P<trial>\d{1})/$', wire.summary_detail),
   url(r'^(?P<obj_type>\w+)/(?P<year>\d{4})-(?P<month>\d{2})-(?P<day>\d{2})/(?P<trial>\d{1})/$', wire.obj_view),
   url(r'^(?P<obj_type>\w+)/$', wire.obj_view_redirect, name='obj_view_redirect'),
   
   
)