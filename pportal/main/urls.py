from django.conf.urls.defaults import patterns, include, url

urlpatterns = patterns('pportal.main.views',
    (r'^$', 'main'),
    (r'^formpull$', 'form_pull'),
    (r'^formplay/(?P<form_id>.*)$', 'form_play'),
    (r'^debug/clearforms$', 'clear_forms'),
)
