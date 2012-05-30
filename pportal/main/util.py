import webservices as ws
import crf_to_xform as convert
from django.conf import settings
import ocxforms.util as u
from touchforms.formplayer.models import XForm
import collections

def study_export():
    conn = ws.connect(settings.WEBSERVICE_URL, ws.STUDY_WSDL)
    ws.authenticate(conn, (settings.OC_USER, settings.OC_PASS))
    return ws.study_export(conn, settings.STUDY_NAME)

def pull_latest():
    export = study_export()
    if not export:
        raise RuntimeError('error querying web service')

    xforms = [u.dump_xml(xf, True) for xf in [convert._convert_xform(export)]] # convert_xform will eventually return a list
    for xf in xforms:
        update_xform(xf)

def update_xform(xform):
    XForm.from_raw(xform)

def get_latest():
    # inefficient
    latest = map_reduce(XForm.objects.all(), lambda xf: [(xf.namespace, xf)], lambda v: max(v, key=lambda xf: xf.created)).values()
    def reduce_xf(xf):
        return {'name': xf.name, 'id': xf.id, 'xmlns': xf.namespace}
    return [reduce_xf(xf) for xf in latest]




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
