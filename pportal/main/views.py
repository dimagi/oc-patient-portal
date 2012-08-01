from django.template import RequestContext
from django.http import HttpResponse, HttpResponseRedirect, HttpResponseNotFound, HttpResponseForbidden
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

@login_required
def home(request):
    if request.user.is_staff:
        return render(request, 'admin_landing.html', {})
    else:
        return render(request, 'participant_landing.html', {})

@login_required
def manage_users(request):
    if not request.user.is_staff:
        return HttpResponseForbidden('admin access required')

    return render(request, 'manage_users.html', {
            'formlist': json.dumps(util.get_latest()),
        })

@login_required
def manage_forms(request):
    if not request.user.is_staff:
        return HttpResponseForbidden('admin access required')

    return render(request, 'manage_forms.html', {
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
    return HttpResponse(json.dumps(list(util.get_subjects(study_id))), 'text/json')

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

@csrf_exempt
def gen_reg_code(request):
    subject_id = request.POST.get('subj_id')
    study_name = request.POST.get('study')
    code = util.gen_reg_code()

    pending_reg = PendingRegistration()
    pending_reg.subj_id = subject_id
    pending_reg.study_name = study_name
    pending_reg.reg_code = code
    pending_reg.save()

    return HttpResponse(json.dumps({'code': code}), 'text/json')

def validate_reg_code(request):
    code = request.GET.get('code')

    #normalize
    code = ''.join(c for c in code if c in '0123456789')

    try:
        pend = PendingRegistration.objects.get(reg_code=code)
        status = 'valid'
    except PendingRegistration.DoesNotExist:
        status = 'invalid'

    return HttpResponse(json.dumps({'status': status, 'code': code}), 'text/json')
    
# we should be doing validation!
def register_user(request):
    u = User()
    u.email = request.POST.get('email').strip()
    u.username = u.email
    u.first_name = request.POST.get('fname').strip()
    u.last_name = request.POST.get('lname').strip()
    u.set_password(request.POST.get('pass'))

    pend = PendingRegistration.objects.get(reg_code = request.POST.get('regcode'))
    up = UserProfile()
    up.user = u
    up.subject_id = pend.subj_id
    up.study_name = pend.study_name
    up.full_name = '%s %s' % (u.first_name, u.last_name)
    up.display_name = u.first_name

    # transaction?
    u.save()
    up.save()
    pend.delete()

    return HttpResponseRedirect('/')
