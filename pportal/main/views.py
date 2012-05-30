from django.template import RequestContext
from django.http import HttpResponse, HttpResponseRedirect, HttpResponseNotFound
from django.shortcuts import render, get_object_or_404, redirect
from django.conf import settings
from django.contrib.auth.decorators import login_required
from django.core.urlresolvers import reverse

def main(request):
    return render(request, 'main.html', {'asdf': [1,2,3,4]})
