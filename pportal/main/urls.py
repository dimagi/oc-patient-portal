from django.conf.urls.defaults import patterns, include, url

urlpatterns = patterns('pportal.main.views',
    (r'^$', 'main'),
    (r'^admin$', 'form_admin'),
    (r'^studies$', 'get_studies'),
    (r'^formpull/(?P<study_id>.*)$', 'form_pull'),
    (r'^formplay/(?P<form_id>.*)$', 'form_play'),
    (r'^debug/clearall$', 'clear_all'),
    (r'^debug/clearstudy/(?P<study_id>.*)$', 'clear_study'),
)
