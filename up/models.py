# coding:utf-8
from django.db import models
from django.utils import timezone

# Create your models here.
class Upfile(models.Model):
    file_name = models.CharField(max_length = 30)
    file_path = models.FileField(upload_to = './upload/')
    file_descr = models.TextField(default = 'there is no description')
    created_date = models.DateTimeField(default = timezone.now)

    if_anal = models.CharField(max_length = 30,default = 'False')
    anal_date = models.DateTimeField(default = timezone.now)
    #result_path = file_path = models.FileField(default = './out/')

    def __unicode__(self):
        return self.username

#TOPIC_CHOICES = (
#        ('leve1', '差评'),
#        ('leve2', '中评'),
#        ('leve3', '好评'),
#)
