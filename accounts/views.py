# coding:utf-8
from django.shortcuts import render_to_response,render,get_object_or_404,redirect, urlresolvers
from django.http import HttpResponse, HttpResponseRedirect,JsonResponse 
from django.contrib import auth
from django.contrib.auth import authenticate, login
from django.contrib.auth.decorators import login_required,permission_required
from django.contrib.auth.models import User,Group,Permission 
from django.contrib.contenttypes.models import ContentType
from django.contrib import messages
from django.template.context import RequestContext
from django.utils import timezone
from django.db.models import Q
import time
import datetime
import os
import pandas as pd #除了pip安装pandas,还要安装xlrd、xlwt以进行excel读写
import numpy as np
import random

import re
import json
from django.http import JsonResponse 

from django.forms.formsets import formset_factory
from django.core.paginator import Paginator, PageNotAnInteger, EmptyPage

from django.utils.encoding import smart_str
#from bootstrap_toolkit.widgets import BootstrapUneditableInput
from .models import *
from .forms import *



#下载文件
def readFile(filename,chunk_size=512):
    with open(filename,'rb') as f:
        while True:
            c=f.read(chunk_size)
            if c:
                yield c
            else:
                break
def downloadfile(fpath,fname):
    filepath = str(fpath )+str(fname ) #文件在根目录下的examples目录下，且名字就是超链接传递过来
    data = readFile(filepath)
    response = HttpResponse(data,content_type='application/octet-stream') 
    response['Content-Disposition'] = 'attachment; filename=%s' % fname
    return response           
#取字符串中两个符号之间的东东
def txt_wrap_by( start_str, end, html):
    start = html.find(start_str)
    if start >= 0:
        start += len(start_str)
        end = html.find(end, start)
        if end >= 0:
            return html[start:end].strip()
@login_required
def downtemplate(request,pp):
    generate_user = request.user.username
    #用户合法
    user = User.objects.get(username__exact= generate_user)
    filename =  pp #超链接传递过来的文件名字
    if user is not None and user.is_active:        
        fpath = './examples/' #文件在根目录下的examples目录下，且名字就是超链接传递过来
        fname = str( filename)+'.xls'
        downfile = downloadfile(fpath,fname)
        return downfile
def handle_uploaded_file(file, filename, filepath):
    file_name = ""
    try:
        if not os.path.exists(filepath):
            os.makedirs(filepath)
        with open(filepath  + filename, 'wb+') as destination:
            for chunk in file.chunks():
                destination.write(chunk)
            destination.close()
    except :
        print('error') 
    return file_name

#用户归于某组,并赋予组权限
def give_group_permission(username, gname):
    if gname == 'student':
        groupname = 'group_student'
        per_codename = 'cando_student'
        per_name = '具有学生权限'
    elif gname == 'teacher':
        groupname = 'group_teacher'
        per_codename = 'cando_teacher'
        per_name = '具有教师权限'
    elif gname == 'admin':
        groupname = 'group_admin'
        per_codename = 'cando_admin'
        per_name = '具有学校管理权限'
    #用户组是否存在
    try:#用户组存在,给用户赋予组和权限
        group = Group.objects.get(name=groupname)
        user = User.objects.get(username=username)
        user.groups.add(group)#用户加入用户组                   
        groupperms = Permission.objects.get(codename=per_codename)
        user.user_permissions.add(groupperms)#给用户赋予组权限
        user.save()
    except:#不存在则创建组,创建权限,赋予组
        group = Group.objects.create(name=groupname)
        #contentType = ContentType.objects.get(app_label='accounts', model='User')
        contentType = ContentType.objects.get_for_model(User)
        groupperms = Permission.objects.create(codename=per_codename,
                                       name=per_name,
                                       content_type=contentType)
        group.permissions.add(groupperms)#给组赋予权限
        group.save()
        #用户组创建完成,给用户赋予组和权限
        group = Group.objects.get(name=groupname)
        user = User.objects.get(username=username)
        user.groups.add(group)#用户加入用户组                   
        groupperms = Permission.objects.get(codename=per_codename)
        user.user_permissions.add(groupperms)#给用户赋予组权限
        user.save()



#注册页面选择区县
def sel_city(request):
    #初次访问
    if request.method == 'GET':
        sheng = Sheng.objects.all()
        shi = []
        qu = []
        has_sheng = False
        has_shi = False
        has_qu = False
        return render_to_response('accounts/before_register.html', RequestContext(request, {
            'sheng': sheng,
            'has_sheng': has_sheng,
            'has_shi': has_shi,
            'has_qu': has_qu,
            }))
    #已经提交数据
    else:
        sheng = request.POST.get('province', '')
        shi =  request.POST.get('city', '')
        qu =  request.POST.get('district', '')
        xiao =  request.POST.get('school', '')
        has_sheng = False
        has_shi = False
        has_qu = False
        has_xiao = False
        has_other = False
        if len(sheng)>0:#提交了省
            prov = Sheng.objects.get(id=sheng)#选出该省
            has_sheng = True            
            request.session['logined_user_province']=prov.name  #写入session
            shi =  Shi.objects.filter(sheng_id = sheng)#筛选出该省所有市   
            return render_to_response('accounts/before_register.html', RequestContext(request, {
                'sheng': prov,
                'shi': shi,
                'has_sheng': has_sheng,
                'has_shi': has_shi,
                'has_qu': has_qu,
                'has_xiao': has_xiao,
                'has_other': has_other,
                }))
        if len(shi)>0:#提交了市
            city = Shi.objects.get(id=shi)#筛选出该市
            has_sheng = True  
            has_shi = True              
            request.session['logined_user_city']=city.name  #写入session   
            qu =  Qu.objects.filter(shi_id = shi) 
            sheng = request.session.get('logined_user_province','')#此时表单已经没有省,只有从session取 
            prov = Sheng.objects.get(name=sheng) 
            return render_to_response('accounts/before_register.html', RequestContext(request, {
                'sheng': prov,
                'shi': city,
                'qu': qu,
                'has_sheng': has_sheng,
                'has_shi': has_shi,
                'has_qu': has_qu,
                'has_xiao': has_xiao,
                'has_other': has_other,
                }))
        if len(qu)>0:#提交了区
            dist = Qu.objects.get(id=qu)
            has_sheng = True  
            has_shi = True    
            has_qu = True                
            request.session['logined_user_district']=dist.name  #写入session   
            xiao =  Xiao.objects.filter(qu_id = qu)
            sheng = request.session.get('logined_user_province','')#此时表单已经没有省,只有从session取 
            prov = Sheng.objects.get(name=sheng) 
            shi = request.session.get('logined_user_city','')#此时表单已经没有市,只有从session取 
            city = Shi.objects.get(name=shi,sheng__name=sheng) #外链查询
            return render_to_response('accounts/before_register.html', RequestContext(request, {
                'sheng': prov,
                'shi': city,
                'qu': dist,
                'xiao': xiao,
                'has_sheng': has_sheng,
                'has_shi': has_shi,
                'has_qu': has_qu,
                'has_xiao': has_xiao,
                'has_other': has_other,
                }))
        if len(xiao)>0:#提交了校
            sch = Xiao.objects.get(id=xiao)
            has_sheng = True  
            has_shi = True    
            has_qu = True    
            has_xiao = True                 
            request.session['logined_user_school']=sch.name  #写入session 
            sheng = request.session.get('logined_user_province','')#此时表单已经没有省,只有从session取 
            prov = Sheng.objects.get(name=sheng) 
            shi = request.session.get('logined_user_city','')#此时表单已经没有市,只有从session取 
            city = Shi.objects.get(name=shi,sheng__name=sheng) 
            qu = request.session.get('logined_user_district','')#此时表单已经没有市,只有从session取 
            dist = Qu.objects.get(name=qu,shi__name=shi,shi__sheng__name=sheng)#外链的外链查询 
            return render_to_response('accounts/before_register.html', RequestContext(request, {
                'sheng': prov,
                'shi': city,
                'qu': dist,
                'xiao': sch,
                'has_sheng': has_sheng,
                'has_shi': has_shi,
                'has_qu': has_qu,
                'has_xiao': has_xiao,
                'has_other': has_other,
                }))



def signup(request): 
    #初次访问
    if request.method == 'GET':        
        return render_to_response('signupfirst.html', RequestContext(request, {    })) 
    else:
        if request.method == 'POST':  
            schoolcode = request.POST.get('schoolcode', '')
            errmsg = ' '
            regform = RegisterForm()
            if schoolcode == '123':    # success
                errmsg = ' 授权学校：管理员'
                return render_to_response('signup.html', RequestContext(request, {'form': regform,'errmsg': errmsg,}))
            elif schoolcode == '':# failed
                errmsg = '授权码不能为空'
                return render_to_response('signupfirst.html', RequestContext(request, {'errmsg': errmsg,}))
            else:   # failed
                errmsg = '授权码错误'
                return render_to_response('signupfirst.html', RequestContext(request, {'errmsg': errmsg,})) 

def register(request): 
    #初次访问
    if request.method == 'GET':        
        return render_to_response('signup.html', RequestContext(request, {    }))
    #已经提交数据
    else:
        regform = RegisterForm(request.POST)
        if regform.is_valid():
            username = request.POST.get('username', '')
            clarkno = request.POST.get('clarkno', '')
            password1 = request.POST.get('password1', '')
            password2 = request.POST.get('password2', '')
            truename = request.POST.get('truename', '')
            inyear = request.POST.get('inyear', '')
            work = request.POST.get('work', '')
            email = request.POST.get('email', '')
            phone = request.POST.get('phone', '')
            birthday = request.POST.get('birthday', '')
            gender = request.POST.get('gender', '')

            codereturn = request.POST.get('codereturn', '123')
            #验证码是否返回
            if len(codereturn) == 0 or int(thecode) - int(codereturn) > 5:#不超过5分钟验证码有效
                errmsg = '验证不通过，验证滑块有效期5分钟'
                return render_to_response('login.html', RequestContext(request, {'codereturn': codereturn,'thecode': thecode,
                    'form': loginform,
                    'errmsg': errmsg,}))#验证不通过
            #用户名是否被占用
            user = User.objects.filter(username=username)
            if user.count():
                errmsg = '用户名被占用'
                return render_to_response('signup.html', RequestContext(request, {'form': regform,'errmsg': errmsg,}))
            #注册成功
            profile = User.objects.create_user( username, email, password1 )
            profile.username=username 
            profile.clarkno=clarkno 
            profile.truename=truename 
            profile.inyear=inyear 
            profile.work=work 
            profile.phone=phone 
            profile.gender=gender 
            profile.birthday=birthday
            profile.xiao = request.session.get('logined_user_school','') 
            profile.qu = request.session.get('logined_user_district','')
            profile.shi = request.session.get('logined_user_city','')
            profile.sheng = request.session.get('logined_user_province','')
            profile.usergroup = 'group_student' #默认以学生角色注册 
            profile.creator_name = 'register'  
            profile.creator_time = timezone.now()  
            profile.save()  
            request.session['logined_user_truename']= truename  #写入session 
            give_group_permission(username,'student')
            
            #自动登录
            user = auth.authenticate(username=username, password=password1)#登录前需要先验证  
            if user is not None and user.is_active:
                auth.login(request, user) 
                return render_to_response('accounts/message.html', RequestContext(request, {'form': regform,'words':'注册成功', 'urlname':'/',}))          
        else:
            #尚未填写注册表格
            errmsg = '请完整填写下面表格'
            return render_to_response('signup.html', RequestContext(request, {'form': regform,'errmsg': errmsg,}))        




def teacherreg(request): 
    #初次访问
    if request.method == 'GET':  
        regform = RegisterForm()      
        return render_to_response('teacherreg.html', RequestContext(request, { 'form': regform,   }))
    else:         
        regform = RegisterForm()      
        return render_to_response('teacherreg2.html', RequestContext(request, { 'form': regform,   }))

def help(request): 
    return render_to_response('help.html', RequestContext(request, {}))




def form_validation(request): 
    return render_to_response('form_validation.html', RequestContext(request, {}))


def login(request):
    #初次访问
    if request.method == 'GET':
        return render_to_response('login.html', RequestContext(request, {}))
    
    #已经post提交数据
    elif request.method == 'POST':
        loginform = LoginForm(request.POST)
        if loginform.is_valid():
            username = request.POST.get('username', '')
            password = request.POST.get('password', '')
            user = auth.authenticate(username=username, password=password)
            if user is not None and user.is_active:
                #登录成功
                auth.login(request, user) 
                #为超级用户更新用户与信息
                susers = User.objects.filter(is_superuser = '1')
                for suser in susers:
                    if suser.xiao_name == None:       
                        suser.xiao_name = '超级单位'       
                        suser.xiao_id = '000'
                        suser.qu_name = '超级区县'
                        suser.shi_name = '超级地市'
                        suser.sheng_name = '超级省份'
                        suser.truename = '超级管理员'
                        suser.usergroup = 'group_admin'
                        suser.birthday = '1980-04-17'
                        suser.save() 
                         
                user = User.objects.get(id=request.user.id) 
                user_name = str(user.username)                       
                user_school = user.xiao_name                      
                user_schoolid = user.xiao_id
                user_district = user.qu_name
                user_city = user.shi_name
                user_province = user.sheng_name
                user_true_name = str(user.truename)
                user_group = str(user.usergroup)
                user_birth = str(user.birthday)  
                dict_of_user_info = {
                            'user_name':user_name,
                            'user_school':user_school,
                            'user_district':user_district,
                            'user_city':user_city,
                            'user_province':user_province,
                            'user_true_name':user_true_name,
                            'user_group':user_group,
                            'user_birth':user_birth,
                            }  

   
                #return render_to_response('index.html', RequestContext(request, {'dict_of_user_info':json.dumps(dict_of_user_info),}))    
                return redirect('homepage')


            else:
                #登录失败
                errmsg = '用户名或密码错误'
                return render_to_response('login.html', RequestContext(request, {'form': loginform,'errmsg': errmsg}))
        else:
            #form无效
            errmsg = '填写不完整'
            return render_to_response('login.html', RequestContext(request, {'form': loginform,'errmsg': errmsg}))

def get_site_info(userid):
    user = User.objects.get(id= userid)
    #************************* 首页需要显示的数据*************************
    users = User.objects.filter(usergroup__in =('group_student' ,'group_teacher'))
    stus = User.objects.filter(usergroup='group_student')
    teas = User.objects.filter(usergroup='group_teacher')
    qnrscount = QnRecord.objects.all().count()
    qnscount = Questionare.objects.all().count()

    qns = Questionare.objects.all().order_by('-created_time')[ :5]
    qnrs_me = QnRecord.objects.filter(taker_id_id=user.id).order_by('-taken_time')[ :5]
    user_sch = user.xiao
    user_of_same_sch = User.objects.filter(xiao=user_sch)#同一所学校的所有用户     
    qnrs_sch = QnRecord.objects.filter(taker_id_id__in=user_of_same_sch).order_by('-taken_time')[ :5]
    qnrs_all = QnRecord.objects.all().order_by('-taken_time') 
    dict_of_site_info = {
                        'qnrs_me':qnrs_me,
                        'qnrs_sch':qnrs_sch,
                        'qnrs_all':qnrs_all,
                        'qns':qns,
                        'qnrscount':qnrscount,
                        'qnscount':qnscount,
                        'users':users,
                        'stus':stus,
                        'teas':teas,
                        'user_of_same_sch':user_of_same_sch,
                        }  
    return  json.dumps(dict_of_site_info)     



@login_required
def homepage(request):     
    operator = request.user   

    if operator.is_superuser:
        scores = Score.objects.all().order_by('-created_time') #最近事项
        employee = User.objects.filter( is_active=1).order_by('-times')#常用员工
        employeescore = User.objects.filter( is_active=1).order_by('-scores')#高分员工
        schs = Xiao.objects.all().order_by('-created_time') #机构
        operatorsch = None
    else: 
        operatorsch = Xiao.objects.get(id=operator.xiao_id)
        scores = Score.objects.filter( xiao=operatorsch ).order_by('-created_time') #最近事项
        employee = User.objects.filter(xiao_id=operator.xiao_id,  is_active=1 ).order_by('-times')#常用员工
        employeescore = User.objects.filter(xiao_id=operator.xiao_id,  is_active=1).order_by('-scores')#高分员工
        schs = Xiao.objects.all().order_by('-created_time') #机构

    #初次访问
    if request.method == 'GET': 
        issues = OfenIssue.objects.all().order_by('-created_time')#常用事项
        return render_to_response('index.html', RequestContext(request, {
            'issues':issues,
            'scores':scores,
            'employee': employee,
            'employeescore': employeescore,
            'schs': schs,
            'operatorsch': operatorsch,
            }))
        
                 

'''
def login(request):
    user = request.user
    #userprof = User.objects.get(user_id=user.id)
    #users = User.objects.filter(schoolname=userprof.schoolname,districtname=userprof.districtname,cityname=userprof.cityname,provincename=userprof.provincename)
    users = User.objects.filter(usergroup__in =('group_student' ,'group_teacher'))
    stus = User.objects.filter(usergroup='group_student')
    teas = User.objects.filter(usergroup='group_teacher')
    qnrscount = QnRecord.objects.all().count()
    qnscount = Questionare.objects.all().count()
    
    
    if request.method == 'GET':
        if not user.is_authenticated:#初次访问
            loginform = LoginForm()
            qns = ''
            qnrs = ''
            return render_to_response('login.html', RequestContext(request, {
                'form': loginform,
                'qnrs':qnrs,
                'qns':qns,
                'qnrscount':qnrscount,
                'qnscount':qnscount,
                'users':users,
                'stus':stus,
                'teas':teas,
                }))
        else:#已经登陆,点击首页时也是以request.method == 'GET'方式访问
            loginform = LoginForm()
            qns = Questionare.objects.all().order_by('-created_time')[ :5]
            qnrs_me = QnRecord.objects.filter(taker_id_id=user.id).order_by('-taken_time')[ :5]
            user_sch = request.session.get('logined_user_school')
            taker_of_same_sch = User.objects.filter(schoolname=user_sch)#同一所学校的所有用户
            user_of_same_sch = User.objects.filter(USERPROFILE_FAN_USER__schoolname=user_sch) #同一所学校的所有用户     
            qnrs_sch = QnRecord.objects.filter(taker_id_id__in=user_of_same_sch).order_by('-taken_time')[ :5]
            qnrs_all = QnRecord.objects.all().order_by('-taken_time')


            return render_to_response('login.html', RequestContext(request, {
                        'form': loginform,
                        'qnrs_me':qnrs_me,
                        'qnrs_sch':qnrs_sch,
                        'qnrs_all':qnrs_all,
                        'qns':qns,
                        'qnrscount':qnrscount,
                        'qnscount':qnscount,
                        'users':users,
                        'stus':stus,
                        'teas':teas,
                        'taker_of_same_sch':taker_of_same_sch,
                        'user_of_same_sch':user_of_same_sch,
                        })) 
    #已经post提交数据
    elif request.method == 'POST':
        loginform = LoginForm(request.POST)
        qns = Questionare.objects.all().order_by('-created_time')[ :5]
        if loginform.is_valid():
            username = request.POST.get('username', '')
            password = request.POST.get('password', '')
            #用户名是否存在
            user = User.objects.filter(username=username)
            if not user.count():
                return render_to_response('login.html', RequestContext(request, {'form': loginform,}))
            user = auth.authenticate(username=username, password=password)
            if user is not None and user.is_active:
                #登录成功
                auth.login(request, user)

                #************************* 为superuser创建profile************************* 
                if  user.is_superuser:
                    s_profile = User.objects.filter(user_id= user.id)
                    if not s_profile.count():#尚没有记录创建
                        suser_profile = User()# 
                        suser_profile.user_id=user.id 
                        suser_profile.username=user.username
                        suser_profile.usergroup= 'is_superuser'
                        suser_profile.save()
                #************************* 为superuser创建profile*************************
                user_profile = User.objects.get(user_id= user.id)
                    #把获用户信息传递给session对象
                request.session['logined_user_school'] = user_profile.schoolname
                request.session['logined_user_district'] = user_profile.districtname
                request.session['logined_user_city'] = user_profile.cityname
                request.session['logined_user_province'] = user_profile.provincename
                request.session['logined_user_truename'] = user_profile.truename
                request.session['logined_user_usergroup'] = user_profile.usergroup

                
                qnrs_me = QnRecord.objects.filter(taker_id_id=user.id).order_by('-taken_time')[ :5]
                user_sch = request.session.get('logined_user_school')
                taker_of_same_sch = User.objects.filter(schoolname=user_sch)#同一所学校的所有用户
                user_of_same_sch = User.objects.filter(USERPROFILE_FAN_USER__schoolname=user_sch) #同一所学校的所有用户     
                qnrs_sch = QnRecord.objects.filter(taker_id_id__in=user_of_same_sch).order_by('-taken_time')[ :5]
                qnrs_all = QnRecord.objects.all().order_by('-taken_time')


                return render_to_response('index.html', RequestContext(request, {
                        'form': loginform,
                        'qnrs_me':qnrs_me,
                        'qnrs_sch':qnrs_sch,
                        'qnrs_all':qnrs_all,
                        'qns':qns,
                        'qnrscount':qnrscount,
                        'qnscount':qnscount,
                        'users':users,
                        'stus':stus,
                        'teas':teas,
                        'taker_of_same_sch':taker_of_same_sch,
                        'user_of_same_sch':user_of_same_sch,
                        })) 
                #return HttpResponseRedirect('/', RequestContext(request, {'form': loginform,})) 
            else:
                #登录失败
                return render_to_response('login.html', RequestContext(request, {
                    'form': loginform,
                    'password_is_wrong':True,
                    'qnrscount':qnrscount,
                    'qnscount':qnscount,
                    'users':users,
                    'stus':stus,
                    'teas':teas,
                    }))
        else:
            #form无效
            return render_to_response('login.html', RequestContext(request, {
                'form': loginform,

                'qnrs':qnrs,
                'qns':qns,
                'qnrscount':qnrscount,
                'qnscount':qnscount,
                'users':users,
                'stus':stus,
                'teas':teas,
                }))
'''

@login_required
def logout(request):
    #清理cookie里保存username
    response = HttpResponseRedirect("/")
    if request.COOKIES.get('user_name')!= None :
        response.delete_cookie('user_name')
    '''
    if request.session.get('logined_user_school')!= None :
        del request.session['logined_user_school']  #删除session
    if request.session.get('logined_user_district')!= None :
        del request.session['logined_user_district']
    if request.session.get('logined_user_city')!= None :
        del request.session['logined_user_city']
    if request.session.get('logined_user_province')!= None :
        del request.session['logined_user_province']
    if request.session.get('logined_user_truename')!= None :
        del request.session['logined_user_truename']
    if request.session.get('logined_user_usergroup')!= None :
        del request.session['logined_user_usergroup']
        '''
    auth.logout(request)
    return response

@login_required
def userinfo(request):
    user = request.user
    userprof = User.objects.get(id=user)
    return render_to_response('accounts/userinfo.html', RequestContext(request, {'user': user,'userprof': userprof,}))
@login_required
def changepassword(request):
    #初次访问
    if request.method == 'GET':
        chgform = PasswordForm()
        return render_to_response('accounts/changepassword.html', RequestContext(request, {'form': chgform,}))
    #已经提交数据
    else:
        chgform = PasswordForm(request.POST)
        if chgform.is_valid():
            username = request.user.username
            oldpassword = request.POST.get('oldpassword', '')
            password1 = request.POST.get('newpassword1', '')
            password2 = request.POST.get('newpassword2', '')
            #检查旧密码
            user = auth.authenticate(username=username, password=oldpassword)
            if user is None or not user.is_active:
                #旧密码错误
                return render_to_response('accounts/changepassword.html', RequestContext(request, {'form': chgform,'password_is_wrong':True})) 
            else:
                user = User.objects.get(username__exact= username)
                user.set_password(password1)
                user.save()
                return render_to_response('accounts/message.html', RequestContext(request, {'form': chgform,'words':'修改成功','urlname':'/','urlpara':'',}))                                   
        else:
            return render_to_response('accounts/changepassword.html', RequestContext(request, {'form': chgform,}))

@login_required
def userlistsch(request, schid):
    operator = request.user
    users = User.objects.filter(is_active = 1,xiao_id=schid)
    thissch = Xiao.objects.get(id=schid)
    schs = Xiao.objects.all()
    schsid = []
    schscode = []
    schscode.append(thissch.schcode)
    schsadminname = []
    for san in schs:
        schsadminname.append(san.admin_name)
    if int(thissch.schlevel) < 4:#共4级
        for i in range(int(thissch.schlevel),5):#共4级
            #查找下一级级schcode
            for sch in schs:
                if sch.upschcode in schscode and sch.schlevel == i+1:
                    schscode.append(sch.schcode)

    schscode.remove(thissch.schcode)
    schsbelow = Xiao.objects.filter(schcode__in=schscode)
    for sc in schsbelow:
        schsid.append(sc.id)
    usersbelow = User.objects.filter(is_active = 1,xiao_id__in=schsid)
    return render_to_response('accounts/userlist.html', RequestContext(request, {
        'users': users,
        'usersbelow': usersbelow,
        'schsadminname': schsadminname,
        'schsbelow': schsbelow,
        }))
@login_required
def userlistall(request):
    operator = request.user
    schs = Xiao.objects.all()
    schsadminname = []
    for san in schs:
        schsadminname.append(san.admin_name)
    if  operator.is_superuser:
        users = User.objects.filter(is_active = 1)#
        #elif operator.has_perm('accounts.cando_admin') or operator.has_perm('accounts.cando_teacher'):
    else:
        users = User.objects.filter(is_active = 1,is_superuser=0,
                xiao = operator_profile.xiao,
                districtname = operator_profile.districtname,
                cityname = operator_profile.cityname,
                provincename = operator_profile.provincename
                )

    return render_to_response('accounts/userlist.html', RequestContext(request, {
        'users': users,
        'schsadminname': schsadminname,
        }))
    
@permission_required('user.is_superuser', login_url="/")
def userdeleteall(request): #一次删除全部用户，仅供系统管理员使用
    users = User.objects.all()#
    '''
    for u in users:
        if not u.is_superuser:
            User.objects.get(username=u.username).delete()#删除用户表user的信息
    #因为userprofile是从user外键来的，所以user删除了，userpfofile也就没有了，不用再删除
    '''
    for u in users:
        if not u.is_superuser and u.is_active == 1:
            u.is_active = 0
            u.username = str(u.username)+"删除"
            u.clarkno = int(u.clarkno)*(-1)-int(time.strftime('%Y%m%d%H%M%S'))
            u.save()
            Score.objects.filter(employee=u).delete()
    users_left = User.objects.filter(is_active = 1)#
    return render_to_response('accounts/userlist.html', RequestContext(request, {
        'users': users_left,
        }))
@login_required
def userdelete(request,pp): #一次删除一个用户
    del_user = User.objects.get(id = pp)
    superuser = User.objects.filter(is_superuser = 1)[0:1]
    for u in superuser:
        su = u
    #del_profile = User.objects.get(id = pp)#此处用get方法不能用filter
    try:
        sch = Xiao.objects.get(id = del_user.xiao_id )#获取用户的学校
        if sch.admin == del_user:#如果该用户是学校管理员
            sch.admin = su#更换SchoolInfo中的admin为supersuer
            sch.save()
    except Xiao.DoesNotExist:
        print('no school match this user')
    u = User.objects.get(id = pp)
    u.is_active = 0#假删除
    u.username = str(u.username) + "deleted"
    u.clarkno = int(u.clarkno) - 99999999999999
    u.save()
    Score.objects.filter(employee=u).delete()#删除Score
    
    #User.objects.get(id = pp).delete()#真删除
    #因为userprofile是从user外键来的，所以user删除了，userpfofile也就没有了，不用再删除，否则报错
    
    #users_left = User.objects.filter(is_superuser=0)#
    #userprof_left = User.objects.exclude(usergroup='is_superuser')#
    urlname = "userlistsch"
    urlpara = "/"+str(del_user.xiao_id)+"/"
    return render_to_response('accounts/message.html', RequestContext(request, {'words':'删除成功','urlname':urlname,'urlpara':urlpara,}))   
    
    
    


def forgetpassword(request):
    auth.logout(request)
    return HttpResponseRedirect("/")
#@permission_required('accounts.is_teacher', login_url="/")
@login_required
def addusersch(request,schid):#添加用户，按照单位添加，所有添加的用户都属于这个单位
    operator = request.user
    sch = Xiao.objects.get(id=schid)
    #初次访问
    if request.method == 'GET':
        regform = RegisterForm()
        return render_to_response('accounts/addstu.html', RequestContext(request, {
            'form': regform,
            'sch': sch,
            }))
    #已经提交数据
    else:
        regform = RegisterForm(request.POST)
        if regform.is_valid():
            username = request.POST.get('username', '')
            clarkno = request.POST.get('clarkno', '')
            password1 = request.POST.get('password1', '')
            password2 = request.POST.get('password2', '')
            truename = request.POST.get('truename', '')
            gender = request.POST.get('gender', '')
            birthday = request.POST.get('birthday', '')
            inyear = request.POST.get('inyear', '')
            work = request.POST.get('work', '')
            email = request.POST.get('email', '')
            phone = request.POST.get('phone', '')
            
            usergroup = '员工'
            gname = 'student'

            #用户名是否被占用
            user = User.objects.filter(username=username)
            if user.count():
                return render_to_response('accounts/addstu.html', RequestContext(request, {
                    'form': regform,
                    'operator':operator,
                    }))
            #是否被占用
            user = User.objects.filter(clarkno=clarkno)
            if user.count():
                return render_to_response('accounts/addstu.html', RequestContext(request, {
                    'form': regform,
                    'operator':operator,
                    }))
            else:
                #注册成功
                user = User.objects.create_user( username, email, password1 )
                user.username = username
                user.clarkno = clarkno
                user.truename = truename
                user.gender = gender
                user.birthday = birthday
                user.inyear = inyear
                user.work = work 
                user.phone = phone
                user.sheng_name = sch.sheng.name  
                user.qu_name = sch.qu.name  
                user.shi_name = sch.shi.name  
                user.xiao_id = sch.id    
                user.xiao_name = sch.name 
                user.creator_name = operator.username
                user.created_time = timezone.now()
                user.usergroup = usergroup  
                user.save()  
                #添加成功
                give_group_permission(username,gname)
       
                return render_to_response('accounts/message.html', RequestContext(request, {'words':'添加成功','urlname':'schlist','urlpara':'',}))          
        else:
            return render_to_response('accounts/addstu.html', RequestContext(request, {
                    'form': regform,
                    'sch': sch,
                    }))




#@permission_required('accounts.is_teacher', login_url="/")
@login_required
def impuser(request,schid):#添加用户，包括stu和tea，使用同一个页面
    operator = request.user
    sch = Xiao.objects.get(id=schid)
    #初次访问
    if request.method == 'GET':
        iform = ImpStuForm()
        return render_to_response('accounts/upstus.html', RequestContext(request, {
                'form': iform,
                'operator':operator,
                }))
    #已经post提交数据
    else:
        iform = ImpStuForm(request.FILES)
        if iform.is_valid():
            thefile = request.FILES.get('stufile', None)
            filepath = 'upfiles/user/' + time.strftime('%Y/%m%d%H%M%S/')
            #将文件写入服务端硬盘
            handle_uploaded_file(thefile,str(thefile), filepath) 

    
            df = pd.read_excel(str(filepath)+str(thefile))
            linecount = len(df.index)
            counti = range(linecount)

            imp_username = df['username']#导入的excel文件会自动添加行序号'0 1 2...'作为index
            imp_email = df['email']
            imp_password = df['password'] #是一个series,形式为'index0 value0 index1 value1 ...'            
            imp_name = df['truename']
            imp_phone = df['phone']
            '''
            imp_province = df['province']
            imp_city = df['city']
            imp_district = df['district']
            imp_school = df['company']
            '''
            imp_jobtitle = df['jobtitle']
            imp_staffno = df['staffno']

            usergroup = '员工'
            gname = 'student'
                           


            for i in counti:
                i_username = str(imp_username[i]).strip() #以字典的键名来引用值
                i_email = str(imp_email[i]).strip()
                i_password = str(imp_password[i]).strip()
                i_name = str(imp_name[i]).strip()
                i_phone = str(imp_phone[i]).strip()
                '''
                i_province =  str(imp_province[i]).strip()
                i_city =  str(imp_city[i]).strip()
                i_district = str(imp_district[i]).strip()
                i_school =  str(imp_school[i]).strip()
                '''
                i_jobtitle = str(imp_jobtitle[i]).strip()
                i_staffno = str(imp_staffno[i]).strip()
                '''
                if i_province == '':
                    i_province = operator.sheng_name #获取操作者的
                if i_school == None:
                    i_school = operator.xiao_name #获取操作者的
                if i_district == None:
                    i_district = operator.qu_name #获取操作者的
                if i_city == None:
                    i_city = operator.shi_name #获取操作者的
                '''
                #用户名是否被占用
                user = User.objects.filter(username=i_username)
                if user.count():
                    return render_to_response('accounts/message.html', RequestContext(request, {'words':'用户名被占用','urlname':'javascript:history.go(-1)',})) 
                #是否被占用
                user = User.objects.filter(clarkno=i_staffno)
                if user.count():
                    return render_to_response('accounts/message.html', RequestContext(request, {'words':'工号被占用','urlname':'javascript:history.go(-1)',})) 
                else:
                    #未被占用则创建用户
                    profile = User.objects.create_user( i_username, i_email, i_password )
                    profile.phone=i_phone
                    profile.username=i_username
                    
                    profile.sheng_name = sch.sheng.name
                    profile.shi_name = sch.shi.name
                    profile.qu_name = sch.qu.name
                    profile.xiao_name = sch.name
                    profile.xiao_id = sch.id
                    
                    profile.clarkno = i_staffno
                    profile.work = i_jobtitle
                    
                    profile.truename=i_name
                    profile.creator_name=operator.username
                    profile.creator_time=timezone.now()
                    profile.usergroup= usergroup  
                    profile.save()

                    give_group_permission(i_username,gname)
              
            #添加成功
            return render_to_response('accounts/message.html', RequestContext(request, {'words':'导入用户成功',
                        'urlname':'userlistall',}))
            
        return render_to_response('accounts/message.html', RequestContext(request, {'words':'导入用户失败','urlname':'javascript:history.go(-1)',}))







@login_required
def downtemplate(request,pp):
    generate_user = request.user.username
    #用户合法
    user = User.objects.get(username__exact= generate_user)
    filename =  pp #超链接传递过来的文件名字
    if user is not None and user.is_active:        
        fpath = './examples/'+str( filename )+'.xls' #文件在根目录下的examples目录下，且名字就是超链接传递过来
        fname = str( filename)+'.xls'
        def readFile(fn, buf_size=262144):
            f = open(fn, "rb")
            while True:
                c = f.read(buf_size)
                if c:
                    yield c
                else:
                    break
            f.close()
        data = readFile(fpath)
        response = HttpResponse(data,content_type='application/octet-stream') 
        response['Content-Disposition'] = 'attachment; filename=%s' % fname
        return response


@login_required
def schlist(request):
    schools = Xiao.objects.all()
    if request.user.is_superuser:
        usersch = None
    else:
        usersch = Xiao.objects.get(id=request.user.xiao_id)
    return render_to_response('accounts/schlist.html', RequestContext(request, {
        'schools': schools,
        'usersch': usersch,
        }))
@permission_required('user.is_superuser', login_url="/")
def schdeleteall(request):
    schools = Xiao.objects.all()
    Xiao.objects.all().delete()
    return render_to_response('accounts/schlist.html', RequestContext(request, {
        'schools': schools,
        }))
@permission_required('user.is_superuser', login_url="/")
def schdelete(request,pp):
    schools = Xiao.objects.all()
    school = Xiao.objects.get(id=pp)
    school.delete()
    return render_to_response('accounts/schlist.html', RequestContext(request, {
        'schools': schools,
        }))  
@permission_required('perms.accounts.cando_admin', login_url="/")
def schview(request,pp):
    school = Xiao.objects.get(id=pp)
    return render_to_response('accounts/schview.html', RequestContext(request, {
        'school': school,
        }))      
    

@login_required
def addfirstsch(request):
    operator = request.user
    #初次访问
    if request.method == 'GET':
        theform = AddSchForm()
        upschlevel = 1
        upschcode = 0
        qu_name = operator.qu_name
        shi_name = operator.shi_name
        sheng_name = operator.sheng_name
        return render_to_response('accounts/addsch.html', RequestContext(request, {
            'form': theform,
            'upschlevel': upschlevel,
            'upschcode': upschcode,
            'qu_name': qu_name,
            'shi_name': shi_name,
            'sheng_name': sheng_name,
            }))
    #已经提交数据
    else:
        theform = AddSchForm(request.POST)
        if theform.is_valid():
            schoolname = request.POST.get('school', '')
            districtname = request.POST.get('qu_name', '')
            cityname = request.POST.get('shi_name', '')
            provincename = request.POST.get('sheng_name', '') 
            schoolcode = request.POST.get('schoolcode', '')  
            upschcode = request.POST.get('upschcode', '')  
            upschlevel = request.POST.get('upschlevel', '')         
            #学校名是否被占用
            school = Xiao.objects.filter(
                    Q(name = schoolname),
                    Q(qu__name = districtname),
                    Q(shi__name = cityname),
                    Q(sheng__name = provincename)
                    )
            if school.count():
                return render_to_response('accounts/message.html', RequestContext(request, {'form': theform,'words':'该学校已存在','urlname':'javascript:history.go(-1)',}))
            #省是否存在
            try:
                sheng = Sheng.objects.get(name=provincename)
            except:
                sheng = Sheng()
                sheng.name = provincename
                sheng.save()
                shi = Shi()
                shi.name = cityname
                shi.sheng = sheng
                shi.save()
                qu = Qu()
                qu.name = districtname
                qu.shi = shi
                qu.sheng = sheng
                qu.save()
            #市
            try:
                sheng = Sheng.objects.get(name=provincename)
                shi = Shi.objects.get(name=cityname)
            except:
                shi = Shi()
                shi.name = cityname
                shi.sheng = sheng
                shi.save()
                qu = Qu()
                qu.name = districtname
                qu.shi = shi
                qu.sheng = sheng
                qu.save()
            #区
            try:
                sheng = Sheng.objects.get(name=provincename)
                shi = Shi.objects.get(name=cityname)
                qu = Qu.objects.get(name=districtname)
            except:
                qu = Qu()
                qu.name = districtname
                qu.shi = shi
                qu.sheng = sheng
                qu.save()
            #学校信息
            thesch = Xiao()#e*************************
            thesch.name = schoolname
            thesch.schlevel = schooltype
            thesch.shi = shi
            thesch.qu = qu
            thesch.sheng = sheng
            thesch.creator = operator 
            thesch.creator_name = operator.username 
            thesch.created_time = timezone.now()
            thesch.created_way = 'write'
            thesch.admin = operator
            thesch.admin_name = operator.truename
            thesch.schcode = schoolcode
            thesch.upschcode = upschcode
            thesch.schlevel = int(schlevel)
            thesch.save()    
            '''
            thesch = SchoolInfo()#e************************* 
            thesch.province = provincename
            thesch.school = schoolname
            thesch.schooltype = schooltype
            thesch.city = cityname
            thesch.district = districtname
            thesch.creator = operator.username 
            thesch.created_time = timezone.now()
            thesch.created_way = 'write'
            thesch.admin_name = ''
            thesch.save() 
            ''' 
            #添加成功
            return render_to_response('accounts/message.html', RequestContext(request, {'form': theform,'words':'添加成功',
                        'urlname':'schlist',}))          
        else:
            return render_to_response('accounts/addsch.html', RequestContext(request, {'form': theform,}))    
#@permission_required('accounts.is_teacher', login_url="/")
@login_required
def addsch(request,schid):
    operator = request.user
    #初次访问
    if request.method == 'GET':
        theform = AddSchForm()
        sch = Xiao.objects.get(id=schid)
        upschlevel = int(sch.schlevel)+1
        upschcode = int(sch.schcode)
        qu_name = sch.qu.name
        shi_name = sch.shi.name
        sheng_name = sch.sheng.name
        return render_to_response('accounts/addsch.html', RequestContext(request, {
            'form': theform,
            'upschlevel': upschlevel,
            'upschcode': upschcode,
            'qu_name': qu_name,
            'shi_name': shi_name,
            'sheng_name': sheng_name,
            }))
    #已经提交数据
    else:
        theform = AddSchForm(request.POST)
        if theform.is_valid():
            schoolname = request.POST.get('school', '')
            districtname = request.POST.get('qu_name', '')
            cityname = request.POST.get('shi_name', '')
            provincename = request.POST.get('sheng_name', '') 
            schoolcode = request.POST.get('schoolcode', '')  
            upschcode = request.POST.get('upschcode', '')  
            upschlevel = request.POST.get('upschlevel', '')         
            #学校名是否被占用
            school = Xiao.objects.filter(
                    Q(name = schoolname),
                    Q(qu__name = districtname),
                    Q(shi__name = cityname),
                    Q(sheng__name = provincename)
                    )
            if school.count():
                return render_to_response('accounts/message.html', RequestContext(request, {'form': theform,'words':'该学校已存在','urlname':'javascript:history.go(-1)',}))
            #省是否存在
            try:
                sheng = Sheng.objects.get(name=provincename)
            except:
                sheng = Sheng()
                sheng.name = provincename
                sheng.save()
                shi = Shi()
                shi.name = cityname
                shi.sheng = sheng
                shi.save()
                qu = Qu()
                qu.name = districtname
                qu.shi = shi
                qu.sheng = sheng
                qu.save()
            #市
            try:
                sheng = Sheng.objects.get(name=provincename)
                shi = Shi.objects.get(name=cityname)
            except:
                shi = Shi()
                shi.name = cityname
                shi.sheng = sheng
                shi.save()
                qu = Qu()
                qu.name = districtname
                qu.shi = shi
                qu.sheng = sheng
                qu.save()
            #区
            try:
                sheng = Sheng.objects.get(name=provincename)
                shi = Shi.objects.get(name=cityname)
                qu = Qu.objects.get(name=districtname)
            except:
                qu = Qu()
                qu.name = districtname
                qu.shi = shi
                qu.sheng = sheng
                qu.save()
            #学校信息
            thesch = Xiao()#e*************************
            thesch.name = schoolname
            thesch.schlevel = schooltype
            thesch.shi = shi
            thesch.qu = qu
            thesch.sheng = sheng
            thesch.creator = operator 
            thesch.creator_name = operator.username 
            thesch.created_time = timezone.now()
            thesch.created_way = 'write'
            thesch.admin = operator
            thesch.admin_name = operator.truename
            thesch.schcode = schoolcode
            thesch.upschcode = upschcode
            thesch.schlevel = int(schlevel)
            thesch.save()    
            '''
            thesch = SchoolInfo()#e************************* 
            thesch.province = provincename
            thesch.school = schoolname
            thesch.schooltype = schooltype
            thesch.city = cityname
            thesch.district = districtname
            thesch.creator = operator.username 
            thesch.created_time = timezone.now()
            thesch.created_way = 'write'
            thesch.admin_name = ''
            thesch.save() 
            ''' 
            #添加成功
            return render_to_response('accounts/message.html', RequestContext(request, {'form': theform,'words':'添加成功',
                        'urlname':'schlist',}))          
        else:
            return render_to_response('accounts/addsch.html', RequestContext(request, {'form': theform,}))
       
@permission_required('user.is_superuser', login_url="/")
def impsch(request):
    operator = request.user
    #初次访问
    if request.method == 'GET':
        iform = ImpStuForm()
        return render_to_response('accounts/upsch.html', RequestContext(request, {'form': iform,}))
    #已经post提交数据
    else:
        iform = ImpStuForm(request.FILES)
        if iform.is_valid():
            thefile = request.FILES.get('stufile', None)
            filepath = 'upfiles/school/' + time.strftime('%Y%m%d/%H%M%S/')
            #将文件写入服务端硬盘
            handle_uploaded_file(thefile,str(thefile), filepath) 

    
            df = pd.read_excel(str(filepath)+str(thefile))
            linecount = len(df.index)
            counti = range(linecount)

            imp_schooltype = df['leveltype']#导入的excel文件会自动添加行序号'0 1 2...'作为index
            imp_province = df['province']          #是一个series,形式为'index0 value0 index1 value1 ...'
            imp_district = df['district']
            imp_city = df['city']
            imp_school = df['company'] 
            imp_code = df['shortcode'] 
            imp_code2 = df['shangjicode']  

            for i in counti:
                i_schooltype = imp_schooltype[i]#以字典的键名来引用值
                i_province =imp_province[i]
                i_school = imp_school[i]
                i_district = imp_district[i]
                i_city = imp_city[i]
                i_code = imp_code[i]
                i_code2 = imp_code2[i]

                shengaaa = Sheng.objects.filter(name=i_province)
                shiaaa = Shi.objects.filter(name=i_city,sheng__name=i_province)
                quaaa = Qu.objects.filter(name=i_district,shi__name=i_city,shi__sheng__name=i_province)

                #学校名是否已经存在
                schoolaaa = Xiao.objects.filter(name = i_school ,qu__name = i_district,qu__shi__name = i_city,qu__shi__sheng__name = i_province )
                if schoolaaa.count():
                    return render_to_response('accounts/message.html', RequestContext(request, {'words':'单位重复,已导入重复前的部分','urlname':'schlist'}))
                else:
                    #省信息
                    if not shengaaa.count():                        
                        sheng = Sheng()
                        sheng.name = i_province
                        sheng.save()
                    #市信息                   
                    if not shiaaa.count():
                        shi = Shi()
                        shi.name = i_city
                        shi.sheng = Sheng.objects.get(name=i_province) 
                        shi.save()
                    #区信息                    
                    if not quaaa.count():
                        qu = Qu()
                        qu.name = i_district
                        qu.shi = Shi.objects.get(name=i_city,sheng__name=i_province)
                        qu.save()
                    #学校信息   
                    thesch = Xiao()#e************************* 
                    thesch.name = i_school
                    thesch.sheng = Sheng.objects.get(name=i_province)
                    thesch.shi = Shi.objects.get(name = i_city,sheng__name = i_province)
                    thesch.qu = Qu.objects.get(name = i_district,shi__name = i_city,shi__sheng__name = i_province)
                    thesch.creator = operator 
                    thesch.creator_name = operator.username 
                    thesch.created_time = timezone.now()
                    thesch.created_way = 'import'
                    thesch.admin = operator
                    thesch.admin_name = operator.truename 
                    thesch.schcode = i_code
                    thesch.schlevel = i_schooltype
                    thesch.upschcode = i_code2
                    thesch.save()  
                    #添加成功
            return render_to_response('accounts/message.html', RequestContext(request, {'words':'导入成功','urlname':'schlist',}))
        return render_to_response('accounts/message.html', RequestContext(request, {'words':'导入失败','urlname':'javascript:history.go(-1)',}))


'''
@permission_required('user.is_superuser', login_url="/")
def createadmin(request,pp):
    operator = request.user
    sch = Xiao.objects.get(id__exact = pp)#注意此处为get方法，而不是filter。get得到一个，而filter得到一串
    sch_sheng = sch.sheng.name
    sch_shi = sch.shi.name
    sch_qu = sch.qu.name
    if not sch is None:
        #初次访问
        if request.method == 'GET':
            regform = RegisterForm()
            return render_to_response('accounts/addstu.html', RequestContext(request, {
                    'form': regform,
                    'sch': sch,
                    }))
        #已经提交数据
        else:
            regform = RegisterForm(request.POST)
            if regform.is_valid():
                username = request.POST.get('username', '')
                clarkno = request.POST.get('clarkno', '')
                password1 = request.POST.get('password1', '')
                password2 = request.POST.get('password2', '')
                truename = request.POST.get('truename', '')
                inyear = request.POST.get('inyear', '')
                work = request.POST.get('work', '')
                email = request.POST.get('email', '')
                phone = request.POST.get('phone', '')
                #用户名是否被占用
                usernew = User.objects.filter(username=username)
                if usernew.count():
                    return render_to_response('accounts/addstu.html', RequestContext(request, {'form': regform,}))
                #注册成功
                user_create = User.objects.create_user( username, email, password1 )
                
                user_create.phone= phone
                user_create.username=username
                user_create.clarkno=clarkno
                user_create.provincename = sch_sheng
                user_create.schoolname =sch.name
                user_create.cityname = sch_shi
                user_create.districtname = sch_qu
                user_create.inyear =inyear
                user_create.work =work
                user_create.truename = truename
                user_create.creator =operator.username
                user_create.usergroup = 'group_admin'
                user_create.save()
                #给用户赋予组和权限
                give_group_permission(username,'admin')
                
                #更新学校管理员信息  
                sch.admin_name = username
                sch.save()
                return render_to_response('accounts/message.html', RequestContext(request, {
                        'form': regform,
                        'sch': sch,
                        'words':'添加成功',
                        'urlname':'schlist',
                        }))          
            else:
                return render_to_response('accounts/addstu.html', RequestContext(request, {
                        'form': regform,
                        'sch': sch,
                        }))
    else:
        return render_to_response('accounts/message.html', RequestContext(request, {                        
                        'words':'school does not exsit',
                        }))    
'''

ONE_PAGE_OF_USER = 9
@permission_required('user.is_superuser', login_url="/")
def chooseadmin(request,pp):
    operator = request.user
    sch = Xiao.objects.get(id__exact = pp)#注意此处为get方法，而不是filter。get得到一个，而filter得到一串
    sch_sheng = sch.sheng
    sch_shi = sch.shi.name
    sch_qu = sch.qu.name
    users = User.objects.filter(is_active=1,xiao_id=sch.id)
    #分页,users
    try:  
        curPage = int(request.GET.get('curPage', '1'))  
        allPage = int(request.GET.get('allPage','1'))  
        pageType = str(request.GET.get('pageType', ''))  
    except ValueError:  
        curPage = 1  
        allPage = 1  
        pageType = ''  
  
    #判断点击了【下一页】还是【上一页】  
    if pageType == 'pageDown':  
        curPage += 1  
    elif pageType == 'pageUp':  
        curPage -= 1  
  
    startPos = (curPage - 1) * ONE_PAGE_OF_USER  
    endPos = startPos + ONE_PAGE_OF_USER  
    
  
    if curPage == 1 and allPage == 1: #标记1  
        allPostCounts =  users.count()#分页,常用事项OfenIssue  
        allPage = int(allPostCounts / ONE_PAGE_OF_USER)   
        remainPost = int(allPostCounts % ONE_PAGE_OF_USER ) 
        if remainPost > 0:  
            allPage += 1 
    if not sch is None:
        #初次访问
        if request.method == 'GET':
            return render_to_response('accounts/selectadmin.html', RequestContext(request, {
                    'users': users[startPos:endPos],
                    'sch': sch,                    
                    'curPage':curPage,#分页
                    'allPage':allPage,
                    }))
        #已经提交数据
        else:
            admin = request.POST.get('employee', '')
            admin2 = request.POST.get('clarkno', '')
            gname = 'admin'#角色
            if admin != '':
                user = User.objects.get(username=admin)
                sch.admin_id = user.id
                sch.admin_name = user.truename
                sch.save()
                give_group_permission(admin,gname)
                return HttpResponseRedirect("schlist")
            elif admin2 != '':
                user = User.objects.get(clarkno=admin2)
                sch.admin_id = user.id
                sch.admin_name = user.truename
                sch.save()
                give_group_permission(user.username,gname)
                return HttpResponseRedirect("schlist")
            else:
                return render_to_response('accounts/selectadmin.html', RequestContext(request, {}))


ONE_PAGE_OF_ISSUE = 6
#@permission_required('accounts.is_teacher', login_url="/")
@login_required
def addscore(request):
    #分页,常用事项OfenIssue
    try:  
        curPage = int(request.GET.get('curPage', '1'))  
        allPage = int(request.GET.get('allPage','1'))  
        pageType = str(request.GET.get('pageType', ''))  
    except ValueError:  
        curPage = 1  
        allPage = 1  
        pageType = ''  
  
    #判断点击了【下一页】还是【上一页】  
    if pageType == 'pageDown':  
        curPage += 1  
    elif pageType == 'pageUp':  
        curPage -= 1  
  
    startPos = (curPage - 1) * ONE_PAGE_OF_ISSUE  
    endPos = startPos + ONE_PAGE_OF_ISSUE  
    
  
    if curPage == 1 and allPage == 1: #标记1  
        allPostCounts =  OfenIssue.objects.all().count()#分页,常用事项OfenIssue  
        allPage = int(allPostCounts / ONE_PAGE_OF_ISSUE)   
        remainPost = int(allPostCounts % ONE_PAGE_OF_ISSUE ) 
        if remainPost > 0:  
            allPage += 1 



    #分页,常用员工User
    try:  
        curPage2 = int(request.GET.get('curPage2', '1'))  
        allPage2 = int(request.GET.get('allPage2','1'))  
        pageType2 = str(request.GET.get('pageType2', ''))  
    except ValueError:  
        curPage2 = 1  
        allPage2 = 1  
        pageType2 = ''  
  
    #判断点击了【下一页】还是【上一页】  
    if pageType2 == 'pageDown':  
        curPage2 += 1  
    elif pageType2 == 'pageUp':  
        curPage2 -= 1  
  
    startPos2 = (curPage2 - 1) * ONE_PAGE_OF_ISSUE  
    endPos2 = startPos2 + ONE_PAGE_OF_ISSUE  
    
  
    if curPage2 == 1 and allPage2 == 1: #标记1  
        allPostCounts2 =  User.objects.all().count()  #分页,常用员工User
        allPage2 = int(allPostCounts2 / ONE_PAGE_OF_ISSUE)  
        remainPost2 = int(allPostCounts2 % ONE_PAGE_OF_ISSUE ) 
        if remainPost2 > 0:  
            allPage2 += 1 



   
    operator = request.user
    if operator.is_superuser:
        scores = Score.objects.all().order_by('-created_time')[0:ONE_PAGE_OF_ISSUE] #最近事项
        empall = User.objects.filter(is_active=1).order_by('truename')
        employee = User.objects.filter(is_active=1).order_by('-times')[startPos2:endPos2]#常用员工
    else:
        operatorsch = Xiao.objects.get(id=operator.xiao_id)
        scores = Score.objects.filter(xiao=operatorsch).order_by('-created_time')[0:ONE_PAGE_OF_ISSUE] #最近事项
        empall = User.objects.filter(is_active=1,xiao_id=operator.xiao_id).order_by('truename')
        employee = User.objects.filter(is_active=1,is_superuser=0,xiao_id=operator.xiao_id).order_by('-times')[startPos2:endPos2]#常用员工
    emplist = []
    for emp in empall:
        emplist.append(str(emp.truename)+"("+str(emp.clarkno)+")")
    isslist = []
    issues = OfenIssue.objects.all().order_by('-created_time')[startPos:endPos]#常用事项emplist = []
    for iss in issues:
        isslist.append(str(iss.issue)+"("+str(iss.scoretype)+str(iss.score)+")")
    #初次访问
    if request.method == 'GET': 
        return render_to_response('accounts/addscore.html', RequestContext(request, {
            'issues':issues,
            'isslist':json.dumps(isslist),
            'scores':scores,
            'employee': employee,
            'emplist': json.dumps(emplist),
            'curPage':curPage,#分页,常用事项OfenIssue
            'allPage':allPage,
            'curPage2':curPage2,#分页,常用员工User
            'allPage2':allPage2,
            }))
    #已经提交数据
    else:
        ####################  先记分        ###################
        oftenissue = request.POST.get('oftenissue', '')#获取事项radio的值
        #判断以哪种方式提交
        if oftenissue == '':#不是以radio选择的方式,还有两外两种:input下拉框c和input填写
            issname = request.POST.get('issname', '')#获取input下拉框的值
            if issname == '':#方式23 以input填写的方式  输入事项
                issue = request.POST.get('issue', '')
                plus = request.POST.get('plus', '')  
                minus = request.POST.get('minus', '') 
                otherwords = request.POST.get('otherwords', '')
                if plus == '':
                    scoretype = '减分'
                    score = minus
                else:
                    scoretype = '加分'
                    score = plus 
                issueobj = OfenIssue() 

            else:#方式21 以input下拉框选择选择的方式   选择事项                
                issnm =  txt_wrap_by( "", "(", issname)        
                issueobj = OfenIssue.objects.get(issue=issnm)
                issue = issueobj.issue
                scoretype = issueobj.scoretype
                score = issueobj.score
                otherwords = ""

        else:#方式22 以radio选择的方式   选择事项
            issueobj = OfenIssue.objects.get(issue=oftenissue)
            issue = issueobj.issue
            scoretype = issueobj.scoretype
            score = issueobj.score
            otherwords = ""
        issueobj.creator =  operator   
        issueobj.created_time = timezone.now()
        issueobj.issue = issue
        issueobj.scoretype = scoretype
        issueobj.score = score
        issueobj.check =  "不需要"
        issueobj.otherwords = otherwords             
        issueobj.times += 1 
        issueobj.save()



        ####################  再记人        ###################
        employeenm = request.POST.get('employee', '')#获取员工radio的值
        if employeenm == '':
            empname = request.POST.get('empname', '')#方式11 以input下拉框的方式  选择员工
            clarknumb =  txt_wrap_by( "(", ")", empname)        
            employee = User.objects.get(clarkno=clarknumb)
        else: #方式12 以radio选择的方式  选择员工
            employee = User.objects.get(username=employeenm)
        otherwords = request.POST.get('otherwords', '')
        xiao = Xiao.objects.get(id=employee.xiao_id)           
        qu = Qu.objects.get(name=employee.qu_name)         
        shi = Shi.objects.get(name=employee.shi_name )       
        sheng = Sheng.objects.get(name=employee.sheng_name)
            
        #信息
        employee.times += 1
        if scoretype == '加分':
            employee.scores += score
        else:
            employee.scores -= score
        employee.save()

        thesch = Score()#e************************* 
        thesch.employee = employee
        thesch.qu = qu
        thesch.shi = shi
        thesch.sheng = sheng
        thesch.xiao = xiao
        thesch.creator = operator 
        thesch.created_time = timezone.now()
        thesch.issue = issue
        thesch.scoretype = scoretype
        thesch.score = score
        thesch.check = ''
        thesch.otherwords = otherwords
        thesch.save()  
        #添加成功
        return render_to_response('accounts/message.html', RequestContext(request, {'words':'添加成功','urlname':'addscore',}))          
    

#@permission_required('accounts.is_teacher', login_url="/")
@login_required
def scorelist(request):
    operator = request.user    
    if operator.is_superuser:
        issues = Score.objects.all().order_by('-created_time')
    else:
        operatorsch = Xiao.objects.get(id=operator.xiao_id)
        issues = Score.objects.filter(xiao=operatorsch).order_by('-created_time')
    return render_to_response('accounts/scorelist.html', RequestContext(request, {'issues':issues,}))

@login_required
def editissue(request):
    operator = request.user       
    theform = OftenIssueForm()
    issues = OfenIssue.objects.all().order_by('-times')
    #初次访问
    if request.method == 'GET': 
        return render_to_response('accounts/issuelist.html', RequestContext(request, {
            'issues':issues,
            'form': theform,
            }))
    #已经提交数据
    else:
        form = OftenIssueForm(request.POST)
        if form.is_valid():
            issue = request.POST.get('issue', '')
            scoretype = request.POST.get('scoretype', '')  
            score = request.POST.get('score', '')
            otherwords = request.POST.get('otherwords', '')          
            check = request.POST.get('check', '') 
            #信息   
            thesch = OfenIssue()
            thesch.creator = operator 
            thesch.created_time = timezone.now()
            thesch.issue = issue
            thesch.scoretype = scoretype
            thesch.score = score
            thesch.check = check
            thesch.otherwords = otherwords
            thesch.save()  
            #添加成功 
            return render_to_response('accounts/message.html', RequestContext(request, {'words':'添加成功','urlname':urlname,'urlpara':'',}))
        else:
            return render_to_response('accounts/message.html', RequestContext(request, {'words':'添加失败','urlname':'javascript:history.go(-1)','urlpara':'',})) 

    issues = OfenIssue.objects.all()
    return render_to_response('accounts/issuelist.html', RequestContext(request, {'issues':issues,'form': theform,}))




def searchuser(request):
    return render_to_response('accounts/chooseuser.html', RequestContext(request, {}))


def mine(request,theuserid):
    operator = User.objects.get(id=theuserid)
    scoresin = Score.objects.filter(employee=operator).order_by('-created_time')
    scoresplus = Score.objects.filter(employee=operator,scoretype="加分").order_by('-created_time')
    plustotal = 0
    for scpl in scoresplus:
        plustotal += int(scpl.score)
    scoresminus = Score.objects.filter(employee=operator,scoretype="减分").order_by('-created_time')
    minustotal = 0
    for scmn in scoresminus:
        minustotal += int(scmn.score)
    scoresout = Score.objects.filter(creator=operator).order_by('-created_time')
    issues = OfenIssue.objects.filter(creator=operator).order_by('-created_time')
    adminsch = Xiao.objects.filter(admin=operator).order_by('-created_time')
    createsch = Xiao.objects.filter(creator=operator).order_by('-created_time')
    return render_to_response('accounts/userinfo.html', RequestContext(request, {
        'operator':operator,
        'scoresin':scoresin,
        'scoresplus':scoresplus,
        'plustotal':plustotal,
        'scoresminus':scoresminus,
        'minustotal':minustotal,
        'scoresout':scoresout,
        'issues':issues,
        'adminsch':adminsch,
        'createsch':createsch,
        }))









