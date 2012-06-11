from django.db import models
from touchforms.formplayer.models import XForm
from xforminst_to_odm import parse_xmlns

class Study(models.Model):
    identifier = models.CharField(max_length=50, unique=True)
    oid = models.CharField(max_length=50, unique=True)
    name = models.CharField(max_length=200)

class StudyEvent(models.Model):
    oid = models.CharField(max_length=50, unique=True)
    name = models.CharField(max_length=200)
    study = models.ForeignKey(Study)

class CRF(XForm):
    event = models.ForeignKey(StudyEvent)

    def __init__(self, *args, **kwargs):
        super(CRF, self).__init__(*args, **kwargs)

        try:
            self.event
        except StudyEvent.DoesNotExist:
            self.event = StudyEvent.objects.get(oid=self.identifiers()['studyevent'])

    def identifiers(self):
        return parse_xmlns(self.namespace)

