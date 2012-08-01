from django.conf.urls.defaults import patterns, include, url

urlpatterns = patterns('pportal.main.views',
    (r'^$', 'home'),

    (r'^manage/participants/$', 'manage_users'),
    (r'^manage/forms/$', 'manage_forms'),

    (r'^participant/(?P<subj_id>.*)/(?P<study_name>.*)$', 'patient_landing'),

    # api calls
    (r'^studies$', 'get_studies'),
    (r'^subjects/(?P<study_id>.*)$', 'get_subjects'),
    (r'^formpull/(?P<study_id>.*)$', 'form_pull'),
    (r'^formplay/(?P<subj_id>.*)/(?P<form_id>.*)/(?P<ordinal>.*)$', 'patient_form_play'),
    (r'^formplay/(?P<form_id>.*)$', 'form_play'),
    (r'^debug/clearall$', 'clear_all'),
    (r'^debug/clearstudy/(?P<study_id>.*)$', 'clear_study'),
    (r'^register/newcode/$', 'gen_reg_code'),
)
