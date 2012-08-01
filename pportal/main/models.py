from django.db import models
from touchforms.formplayer.models import XForm
from xforminst_to_odm import parse_xmlns
from django.contrib.auth.models import User

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
    oid = models.CharField(max_length=50)

    def __init__(self, *args, **kwargs):
        super(CRF, self).__init__(*args, **kwargs)

        try:
            self.event
        except StudyEvent.DoesNotExist:
            self.event = StudyEvent.objects.get(oid=self.identifiers()['studyevent'])

        if not self.oid:
            self.oid = self.identifiers()['form']

    def identifiers(self):
        return parse_xmlns(self.namespace)

class PendingRegistration(models.Model):
    subj_id = models.CharField(max_length=50, primary_key=True)
    study_name = models.CharField(max_length=50)
    reg_code = models.CharField(max_length=50)

class UserProfile(models.Model):
    user = models.OneToOneField(User)

    full_name = models.CharField(max_length=200)
    display_name = models.CharField(max_length=50)
    subject_id = models.CharField(max_length=50)
    study_name = models.CharField(max_length=50)

class CompletionLog(models.Model):
    crf = models.ForeignKey(CRF)
    ordinal = models.IntegerField()
    subject_oid = models.CharField(max_length=50)
    complete_on = models.DateTimeField(auto_now_add=True)
