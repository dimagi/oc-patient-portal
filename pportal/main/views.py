from django.template import RequestContext
from django.http import HttpResponse, HttpResponseRedirect, HttpResponseNotFound
from django.shortcuts import render, get_object_or_404, redirect
from django.conf import settings
from django.contrib.auth.decorators import login_required
from django.views.decorators.csrf import csrf_exempt
from django.core.urlresolvers import reverse
from touchforms.formplayer.models import XForm
import util
import json
from touchforms.formplayer.views import enter_form

def main(request):
    return render(request, 'main.html', {
            'formlist': json.dumps(util.get_latest()),
        })

def form_admin(request):
    return render(request, 'admin.html', {
        })

@csrf_exempt
def form_pull(request):
    errors = util.pull_latest()
    payload = {'forms': util.get_latest(), 'errors': errors}
    return HttpResponse(json.dumps(payload), 'text/json')

@csrf_exempt
def form_play(request, form_id):
    def onsubmit(xform, instance):
        util.submit(instance)
        return HttpResponseRedirect(reverse(main))

    return enter_form(request,
                      xform_id=form_id,
                      input_mode='full',
                      onsubmit=onsubmit)

def get_studies(request):
    return HttpResponse(json.dumps(util.get_studies()), 'text/json')

@csrf_exempt
def clear_forms(request):
    XForm.objects.all().delete()
    return HttpResponse()
