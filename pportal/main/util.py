import webservices as ws
import crf_to_xform as convert
import xforminst_to_odm as odm
from django.conf import settings
import ocxforms.util as u
from touchforms.formplayer.models import XForm
import collections
import logging
from datetime import date, datetime

def study_export():
    conn = ws.connect(settings.WEBSERVICE_URL, ws.STUDY_WSDL)
    ws.authenticate(conn, (settings.OC_USER, settings.OC_PASS))
    return ws.study_export(conn, settings.STUDY_NAME)

def pull_latest():
    export = study_export()
    if not export:
        raise RuntimeError('error querying web service')

    converted, errors = convert._convert_xform(export)
    xforms = [u.dump_xml(xf, True) for xf in converted]

    for xf in xforms:
        update_xform(xf)

    return errors

def update_xform(xform):
    XForm.from_raw(xform)

def get_latest():
    # inefficient
    latest = map_reduce(XForm.objects.all(), lambda xf: [(xf.namespace, xf)], lambda v: max(v, key=lambda xf: xf.created)).values()
    def reduce_xf(xf):
        return {'name': xf.name, 'id': xf.id, 'xmlns': xf.namespace, 'as_of': xf.created.strftime('%Y-%m-%d %H:%M:%S')}
    return [reduce_xf(xf) for xf in latest]

def submit(xfinst):
    resp = odm.process_instance(xfinst, None)

    if resp['odm']:
        logging.debug('converted to odm:\n%s' % u.dump_xml(resp['odm'], pretty=True))

        conn = WSDL(settings.WEBSERVICE_URL)
        auth = (settings.OC_USER, settings.OC_PASS)

        # this is all copied from the uconn proxy; in the end, subjects and study events will already exits/be scheduled
        conn.create_subject(auth, resp['subject_id'], date.today(), resp['birthdate'], resp['gender'], resp['name'], resp['study_id'])
        event_ix = conn.sched_event(auth, resp['subject_id'], resp['studyevent_id'],
                                    resp['location'], resp['start'], resp['end'], resp['study_id'])
        conn.submit(auth, resp['odm'])

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
