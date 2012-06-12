from django.template import RequestContext
from django.http import HttpResponse, HttpResponseRedirect, HttpResponseNotFound
from django.shortcuts import render, get_object_or_404, redirect
from django.conf import settings
from django.contrib.auth.decorators import login_required
from django.views.decorators.csrf import csrf_exempt
from django.core.urlresolvers import reverse
from models import *
import util
import json
from touchforms.formplayer.views import enter_form
import ocxforms.util as u

def landing_page(request):
    return render(request, 'landing.html', {
            'formlist': json.dumps(util.get_latest()),
        })

def patient_landing(request, subj_id, study_name):
    sched_context = util.get_subject_schedule(subj_id, study_name)

    for u in sched_context['upcoming']:
        event = StudyEvent.objects.get(oid=u['event_oid'])
        form = CRF.objects.get(oid=u['form_oid'], event=event)
        u.update({
                'study_name': event.study.name,
                'event_name': event.name,
                'form_name': form.name,
                'form_id': form.id,
            })

    return render(request, 'patient.html', {
            'subject_id': subj_id,
            'context': json.dumps(sched_context),
        })

def form_admin(request):
    return render(request, 'admin.html', {
            'formlist': json.dumps(util.get_latest()),
        })

@csrf_exempt
def form_pull(request, study_id):
    study_id = int(study_id)
    study = Study.objects.get(id=study_id)
    errors = util.pull_latest(study.identifier)
    study_metadata = util.map_reduce(util.get_latest(), lambda s: [(s['id'], s)], lambda v: v[0])[study_id]['events']
    payload = {'study_data': study_metadata, 'errors': errors}
    return HttpResponse(json.dumps(payload), 'text/json')

@csrf_exempt
def form_play(request, form_id):
    def onsubmit(xform, instance):
        odm = util.generate_submit_payload({
                'subject_id': 'SS_123456',
                'event_ordinal': 99,
            }, instance)
        return HttpResponse(u.dump_xml(odm, pretty=True), 'text/xml')

    return enter_form(request,
                      xform_id=form_id,
                      input_mode='full',
                      onsubmit=onsubmit)

@csrf_exempt
def patient_form_play(request, subj_id, form_id, ordinal):
    ordinal = int(ordinal)
    if not ordinal:
        ordinal = None

    def onsubmit(xform, instance):
        odm = util.generate_submit_payload({
                'subject_id': subj_id,
                'event_ordinal': ordinal,
            }, instance)
        util.submit(odm)

        # kind of a hack to get the redirect
        study = Study.objects.get(oid=util._instance_metadata(instance)['study'])
        return redirect(patient_landing, subj_id[len('SS_'):], study.identifier)

    return enter_form(request,
                      xform_id=form_id,
                      input_mode='full',
                      onsubmit=onsubmit)

def get_studies(request):
    util.get_studies()
    return HttpResponse(json.dumps(util.get_latest()), 'text/json')

def get_subjects(request, study_id):
    return HttpResponse(json.dumps(util.get_subjects(study_id)), 'text/json')

@csrf_exempt
def clear_all(request):
    CRF.objects.all().delete()
    StudyEvent.objects.all().delete()
    Study.objects.all().delete()
    return HttpResponse()

@csrf_exempt
def clear_study(request, study_id):
    study_id = int(study_id)
    CRF.objects.filter(event__study__id=study_id).delete()
    StudyEvent.objects.filter(study__id=study_id).delete()
    return HttpResponse()
