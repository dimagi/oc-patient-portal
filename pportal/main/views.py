from django.template import RequestContext
from django.http import HttpResponse, HttpResponseRedirect, HttpResponseNotFound
from django.shortcuts import render, get_object_or_404, redirect
from django.conf import settings
from django.contrib.auth.decorators import login_required
from django.views.decorators.csrf import csrf_exempt
from django.core.urlresolvers import reverse
import util
import json

def main(request):
    return render(request, 'main.html', {
            'formlist': json.dumps(util.get_latest()),
        })

@csrf_exempt
def form_pull(request):
    util.pull_latest()
    return HttpResponse(json.dumps(util.get_latest()), 'text/json')
