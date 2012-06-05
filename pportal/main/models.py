from django.db import models

class Study(models.Model):
    identifier = models.CharField(max_length=50, unique=True)
    oid = models.CharField(max_length=50, unique=True)
    name = models.CharField(max_length=200)

#class StudyEvent(models.Model):
#    pass

#class CRF(models.Model):
#    event = models.ForeignKey(StudyEvent)
#    xform = models.ForeignKey('formplayer.models.XForm')

"""
studyevent:
  id/oid
  name
  study

crf:
  studyevent
  xform
"""
