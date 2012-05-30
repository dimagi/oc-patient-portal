from django.conf.urls.defaults import patterns, include, url

urlpatterns = patterns('pportal.main.views',
    (r'^$', 'main'),
    (r'^formpull', 'form_pull'),
)
