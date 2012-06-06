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

class CRF(models.Model):
    event = models.ForeignKey(StudyEvent)
    xform = models.ForeignKey(XForm)

    def name(self):
        return self.xform.name

    def identifiers(self):
        return parse_xmlns(self.xform.namespace)


