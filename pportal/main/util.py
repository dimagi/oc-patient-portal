import webservices as ws
import crf_to_xform as convert
import xforminst_to_odm as odm
from django.conf import settings
import ocxforms.util as u
from main.models import Study, StudyEvent, CRF
import collections
import logging
from datetime import date, datetime
from ocxforms.crf_to_xform import _
from xml.etree import ElementTree as et
import random
import hashlib

def get_studies():
    conn = ws.connect(settings.WEBSERVICE_URL, ws.STUDY_WSDL)
    ws.authenticate(conn, (settings.OC_USER, settings.OC_PASS))
    studies = ws.list_studies(conn)

    for study in studies:
        try:
            existing = Study.objects.get(oid=study['oid'])
            # TODO: update info here if changed
        except Study.DoesNotExist:
            new_study = Study(**study)
            new_study.save()

    return studies

def get_subjects(study_name):
    conn = ws.connect(settings.WEBSERVICE_URL, ws.SUBJ_WSDL)
    ws.authenticate(conn, (settings.OC_USER, settings.OC_PASS))
    return sorted(ws.all_subjects(conn, study_name))

def study_export(study_name):
    conn = ws.connect(settings.WEBSERVICE_URL, ws.STUDY_WSDL)
    ws.authenticate(conn, (settings.OC_USER, settings.OC_PASS))
    return ws.study_export(conn, study_name)

def pull_latest(study_name):
    export = study_export(study_name)
    if export is None:
        raise RuntimeError('error querying web service')

    converted = convert._convert_xform(export)
    xforms = [u.dump_xml(xf, True) for xf in converted['crfs']]

    for se in converted['study_events']:
        try:
            StudyEvent.objects.get(oid=se['oid'])
            # TODO: update if changed
        except StudyEvent.DoesNotExist:
            new_se = StudyEvent(oid=se['oid'], name=se['name'], study=Study.objects.get(identifier=study_name))
            new_se.save()

    for xf in xforms:
        update_xform(xf)

    return converted['errors']

def update_xform(xform):
    CRF.from_raw(xform)

def get_latest():
    # inefficient
    latest = map_reduce(CRF.objects.all(), lambda xf: [(xf.namespace, xf)], lambda v: max(v, key=lambda xf: xf.created)).values()
    def reduce_xf(xf):
        return {
            'name': xf.name,
            'id': xf.id,
            'oid': xf.identifiers()['form'],
            'xmlns': xf.namespace,
            'as_of': xf.created.strftime('%Y-%m-%d %H:%M:%S'),
            'event_id': xf.event.id
        }
    crfs = [reduce_xf(xf) for xf in latest]
    by_event = map_reduce(crfs, lambda crf: [(crf['event_id'], crf)])
    _events = StudyEvent.objects.all()
    def reduce_event(se):
        return {
            'name': se.name,
            'oid': se.oid,
            'crfs': by_event.get(se.id, []),
            'study_id': se.study.id
        }
    events = [reduce_event(se) for se in _events]
    by_study = map_reduce(events, lambda e: [(e['study_id'], e)])
    _studies = Study.objects.all()
    def reduce_study(st):
        return {
            'name': st.name,
            'id': st.id,
            'oid': st.oid,
            'tag': st.identifier,
            'events': by_study.get(st.id, [])
        }
    studies = [reduce_study(st) for st in _studies]

    return studies

def get_subject_schedule(subject_id, study_id):
    conn = ws.connect(settings.WEBSERVICE_URL, ws.SUBJ_WSDL)
    ws.authenticate(conn, (settings.OC_USER, settings.OC_PASS))
    sched = ws.get_schedule(conn, subject_id, study_id)

    sd = sched.find('.//%s' % _('SubjectData'))
    subj_oid = sd.attrib['SubjectKey']

    def crfs():
        for sed in sd.findall(_('StudyEventData')):
            # ignore study event status for now
            event_oid = sed.attrib['StudyEventOID']
            ordinal = sed.attrib.get('StudyEventRepeatKey')
            if ordinal:
                ordinal = int(ordinal)

            for fd in sed.findall(_('FormData')):
                form_oid = fd.attrib['FormOID']
                status = fd.attrib[_('Status', 'oc')]

                if status == 'not started':
                    yield {'form_oid': form_oid, 'event_oid': event_oid, 'ordinal': ordinal}

    return {
        'subject_oid': subj_oid,
        'upcoming': list(crfs()),
    }

def generate_submit_payload(context, xfinst):
    return odm.process_instance(context, xfinst, None).get('odm')

def submit(odm):
    logging.debug('converted to odm:\n%s' % u.dump_xml(odm, pretty=True))
    conn = WSDL(settings.WEBSERVICE_URL)
    auth = (settings.OC_USER, settings.OC_PASS)
    conn.submit(auth, odm)

def _instance_metadata(inst):
    return odm.parse_metadata(et.fromstring(inst))




class WSDL(object):
    def __init__(self, url):
        def conn(wsdl):
            return ws.connect(url, wsdl)

        self.base_url = url
        self.wsdl = {
            'subj': conn(ws.SUBJ_WSDL),
            'se': conn(ws.SE_WSDL),
            'data': conn(ws.DATA_WSDL),
        }

    def _func(self, f, wsdl, auth):
        conn = self.wsdl[wsdl]
        ws.authenticate(conn, auth)

        def _exec(*args, **kwargs):
            try:
                return f(self.wsdl[wsdl], *args, **kwargs)
            except Exception, e:
                msg = str(e).lower()
                if 'authentication' in msg and 'failed' in msg: #ghetto
                    raise AuthenticationFailed()
                else:
                    raise
        return _exec

    def lookup_subject(self, auth, *args, **kwargs):
        return self._func(ws.lookup_subject, 'subj', auth)(*args, **kwargs)
    def create_subject(self, auth, *args, **kwargs):
        return self._func(ws.create_subject, 'subj', auth)(*args, **kwargs)
    def sched_event(self, auth, *args, **kwargs):
        return self._func(ws.sched, 'se', auth)(*args, **kwargs)
    def submit(self, auth, *args, **kwargs):
        return self._func(ws.submit, 'data', auth)(*args, **kwargs)






def gen_reg_code():
    TOTAL_LEN = 12
    CHKSUM_LEN = 2
    code = ''.join(str(random.randint(0, 9)) for i in range(TOTAL_LEN - CHKSUM_LEN))
    checksum = int(hashlib.sha1(code).hexdigest()[-8:], 16) % 10**CHKSUM_LEN
    return code + ('%0*d' % (CHKSUM_LEN, checksum))


def map_reduce(data, emitfunc=lambda rec: [(rec,)], reducefunc=lambda v: v):
    """perform a "map-reduce" on the data

    emitfunc(datum): return an iterable of key-value pairings as (key, value). alternatively, may
        simply emit (key,) (useful for reducefunc=len)
    reducefunc(values): applied to each list of values with the same key; defaults to just
        returning the list
    data: iterable of data to operate on
    """
    mapped = collections.defaultdict(list)
    for rec in data:
        for emission in emitfunc(rec):
            try:
                k, v = emission
            except ValueError:
                k, v = emission[0], None
            mapped[k].append(v)
    return dict((k, reducefunc(v)) for k, v in mapped.iteritems())
