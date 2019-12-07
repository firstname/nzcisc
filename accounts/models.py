#coding:utf-8
from django.db import models
from django.contrib.auth.models import AbstractUser

# Create your models here.
"""
    自定义权限

class AccessControl(models.Model):
    
    class Meta:
        permissions = (
            ('access_score_manage', u'分数管理'),
            ('access_sch_manage', u'机构管理'),
            ('access_role_manage', u'角色管理'),
            ('access_user_manage', u'用户管理'),
        ) 
   """

#扩展用户信息
class User(AbstractUser):   
    clarkno = models.CharField(u'工号',max_length=30,unique=True,null=True)
    truename = models.CharField(u'姓名',max_length=30,blank=True,null=True)
    gender = models.CharField(u'"男"或"女"',max_length=20,blank=True,null=True,default='') 
    birthday = models.CharField(u'出生日期',max_length=20,blank=True,null=True,default='')
    inyear = models.CharField(u'入职日期',max_length=20,blank=True,null=True,default=' ')  
    work = models.CharField(u'职务',max_length=30,blank=True,null=True,default='销售员')
    phone = models.CharField(u'电话号码',max_length=20,blank=True,null=True)
    '''
    #外键中class必须在之前创建好,才能作为外键使用,否则migrate报错
    #在创建class的实例时,外键相对应的实例也必须已经存在,否则无法创建
    #所以,这里先创建User,后续的class就可以外键User;但User确无法外键后面的class

    qu = models.ForeignKey(Qu,related_name="User_fancha_QU")#外键尚未创建,migrate会报错
    shi = models.ForeignKey(Shi,related_name="User_fancha_SHI")#外键尚未创建,migrate会报错
    sheng = models.ForeignKey(Sheng,related_name="User_fancha_SHENG")#外键尚未创建,migrate会报错
    xiao = models.ForeignKey(Xiao,related_name="User_fancha_XIAO") #外键尚未创建,migrate会报错
    '''
    xiao_id = models.IntegerField(u'单位ID',blank=True,null=True)
    xiao_name = models.CharField(u'单位',max_length=30,blank=True,null=True)
    qu_name = models.CharField(u'区县',max_length=30,blank=True,null=True)
    shi_name = models.CharField(u'地市',max_length=30,blank=True,null=True)
    sheng_name = models.CharField(u'省份',max_length=30,blank=True,null=True)
    usergroup = models.CharField(u'"老师"或"学生"',max_length=20,blank=True,null=True,default='group_student') 
    #creator = models.ForeignKey(User,related_name="creator_fancha_User")
    creator_name = models.CharField(u'创建者',max_length=30,blank=True,null=True)
    created_time = models.CharField(u'创建时间',max_length=30,blank=True,null=True)
    times = models.IntegerField(u'记分次数',blank=True,null=True,default="0")
    scores = models.IntegerField(u'分数',blank=True,null=True,default="0")   
    level = models.CharField(u'等级',max_length=30,blank=True,null=True,default='初级工')
    thumb = models.CharField(u'头像地址',max_length=50,blank=True,null=True,default='')      


class Sheng(models.Model):
    name = models.CharField(max_length=30,blank=True,null=True)

class Shi(models.Model):
    name = models.CharField(max_length=30,blank=True,null=True)
    sheng = models.ForeignKey(Sheng,related_name="SHI_fancha_SHENG")

class Qu(models.Model):
    name = models.CharField(max_length=30,blank=True,null=True)
    shi = models.ForeignKey(Shi,related_name="QU_fancha_SHI")  

class Xiao(models.Model):
    name = models.CharField(u'单位',max_length=30,blank=True,null=True)
    qu = models.ForeignKey(Qu,related_name="XIAO_fancha_QU")
    shi = models.ForeignKey(Shi,related_name="XIAO_fancha_SHI")
    sheng = models.ForeignKey(Sheng,related_name="XIAO_fancha_SHENG") 
    creator = models.ForeignKey(User,related_name="Xiaocreator_fancha_User")
    creator_name= models.CharField(u'创建者',max_length=30,blank=True,null=True)
    created_time = models.CharField(u'创建时间',max_length=30,blank=True,null=True)
    admin = models.ForeignKey(User,related_name="Xiaoadmin_fancha_User")
    admin_name= models.CharField(u'管理员',max_length=30,blank=True,null=True)
    created_way = models.CharField(u'创建方式',max_length=30,blank=True,null=True)
    schlevel = models.IntegerField(u'单位等级',blank=True,null=True)
    schcode = models.IntegerField(u'单位代码注册口令',unique=True,null=True)
    upschcode = models.IntegerField(u'上级单位代码注册口令',blank=True,null=True)
    def __unicode__(self):
        return self.name 

 

class Score(models.Model):
    employee = models.ForeignKey(User,related_name="employee_fancha_User")
    #employee = models.CharField(u'工号',max_length=30,blank=True,null=True)
    '''
    xiao = models.CharField(u'单位',max_length=30,blank=True,null=True)
    qu = models.CharField(u'区县',max_length=30,blank=True,null=True)
    shi = models.CharField(u'地市',max_length=30,blank=True,null=True)
    sheng = models.CharField(u'省份',max_length=30,blank=True,null=True)
    '''
    qu = models.ForeignKey(Qu,related_name="Score_fancha_QU")
    shi = models.ForeignKey(Shi,related_name="Score_fancha_SHI")
    sheng = models.ForeignKey(Sheng,related_name="Score_fancha_SHENG")
    xiao = models.ForeignKey(Xiao,related_name="Score_fancha_XIAO") 
    creator = models.ForeignKey(User,related_name="Score_fancha_User2")
    created_time = models.CharField(u'操作时间',max_length=30,blank=True,null=True)
    issue = models.TextField(u'事件',max_length=30,blank=True,null=True)
    scoretype = models.CharField(u'加减',max_length=30,blank=True,null=True,default="加分")
    score = models.IntegerField(u'分数',blank=True,null=True)
    check = models.CharField(u'审核',max_length=30,blank=True,null=True)
    otherwords = models.TextField(u'备注',max_length=30,blank=True,null=True)
    def __unicode__(self):
        return self.id 

class OfenIssue(models.Model):
    creator = models.ForeignKey(User,related_name="Issue_fancha_User")
    created_time = models.CharField(u'操作时间',max_length=30,blank=True,null=True)
    issue = models.CharField(u'事件',max_length=30,blank=True,null=True)
    scoretype = models.CharField(u'加减',max_length=30,blank=True,null=True)
    score = models.IntegerField(u'分数',blank=True,null=True)
    check = models.CharField(u'审核',max_length=30,blank=True,null=True)
    otherwords = models.TextField(u'备注',max_length=30,blank=True,null=True)
    times = models.IntegerField(u'记分次数',blank=True,null=True,default="0")
    def __unicode__(self):
        return self.id


'''
class UserForeign(AbstractUser): 
    user = models.ForeignKey(User,related_name="user_fancha_User")
    qu = models.ForeignKey(Qu,related_name="fancha_QU")#如果外键尚未创建,migrate会报错
    shi = models.ForeignKey(Shi,related_name="fancha_SHI")#如果外键尚未创建,migrate会报错
    sheng = models.ForeignKey(Sheng,related_name="fancha_SHENG")#如果外键尚未创建,migrate会报错
    xiao = models.ForeignKey(Xiao,related_name="xiao") #如果外键尚未创建,migrate会报错
    creator = models.ForeignKey(User,related_name="creator_fancha_User")
'''












