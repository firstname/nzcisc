#coding = utf-8
from django.shortcuts import render,render_to_response, get_object_or_404
from django import forms
from django.http import HttpResponse,StreamingHttpResponse
from up.models import Upfile
from django.utils import timezone
import pandas as pd #除了pip安装pandas,还要安装xlrd、xlwt以进行excel读写
import re

# Create your views here.
def home(request):
    return render(request, 'index.html', {'firstwords':'我就是我,颜色不一样的焰火'})

class UserForm(forms.Form):
    username = forms.CharField(label="Name the file ",help_text="  ",max_length=20,min_length=2,error_messages={"required":u"不可空","min_length":u"最小长度2","max_length":u"最大长度20"})
    headImg = forms.FileField(label="Choose file ",help_text="  ")
    file_descr = forms.CharField(label='File description',help_text="  ",widget=forms.Textarea)
    #topic = forms.ChoiceField(choices=TOPIC_CHOICES,label='选择评分') #topic中的choices需要在models.py中定义一个数组
    #cc_myself = forms.BooleanField(required=False ,label='订阅该贴')

def register(request):
    if request.method == "POST":
        uf = UserForm(request.POST,request.FILES)
        if uf.is_valid():
            #获取表单信息
            username = uf.cleaned_data['username']
            headImg = uf.cleaned_data['headImg']
            created_date = timezone.now()
            file_descr = uf.cleaned_data['file_descr']
            #写入数据库
            infile = Upfile()
            infile.file_name = username
            infile.file_path = headImg
            infile.created_date = created_date
            infile.file_descr = file_descr
            infile.if_anal = ''
            infile.anal_date = created_date            #infile.result_path = './out/'
            infile.save()            
            return render(request, 'upload_finish.html', {'filename': username,
                'created_date':created_date})
    else:
        uf = UserForm()
    return render(request,'upload.html',{'uf':uf})


def post_list(request):
    posts = Upfile.objects.filter(created_date__lte=timezone.now()).order_by('-created_date')#连字符“-”在“created_date”前表示降序排列。
    return render(request, 'post_list.html', {'posts':posts})

def post_delete(request,pp):
    post = get_object_or_404(Upfile, pk=pp)
    #更新数据库
    post.delete()
    #Upfile.save() 
    return HttpResponse('Delete finished.')

def choose_var(request, pp, ana):
    post = get_object_or_404(Upfile, pk=pp)
    ana_pass = ana
    fpath = './'+str( post.file_path )
    df = pd.read_excel(fpath)
    varname = df.columns
    return render(request, 'var_list.html', {'post': post,
                                             'ana_pass': ana_pass,
                                             'vars': varname})

def vars_detail(request, pp, p1):
    post = get_object_or_404(Upfile, pk=pp)
    fpath = './'+str( post.file_path )
    df = pd.read_excel(fpath)
    cnts = df[p1].value_counts()
    return render(request, 'var_detail.html', {'post': post,
                                                'var': p1,
                                                'cnts':cnts})

def analysis(request, pp, course, ana):
    get_ana = ana
    post = get_object_or_404(Upfile, pk=pp)
    fpath = './'+str( post.file_path )
    opath = './upload/out/'
    df = pd.read_excel(fpath) 
    if ana == 'des':
        vrbs =  '"'+str(course)+'"' 
        outs = descri(df,vrbs,opath,'des_%s' % pp)#必须加引号
        #'["yw","yy","ws","ls","wz","lz","zf"]'
        #"zf"
        #更新数据库
        post.anal_date = timezone.now()
        post.if_anal = post.if_anal+'des,'
        post.save() 
    if ana == 'std':
        vrbs =  course 
        outs = stdscore(df,vrbs,opath,'std_%s' % pp)#必须加引号
        #更新数据库
        post.anal_date = timezone.now()
        post.if_anal = post.if_anal+'std,'
        post.save()         
    return render(request, 'analysis_finish.html', {'post': post,
                                                    'get_ana': get_ana,
                                                    'outs': outs})

def pre_analysis(request, pp):
    post = get_object_or_404(Upfile, pk=pp)
    return render(request, 'analysis_data.html', {'post': post})

def auto_analysis(request, pp,  ana):
    get_ana = ana
    post = get_object_or_404(Upfile, pk=pp)
    fpath = './'+str( post.file_path )
    opath = './upload/out/'
    df = pd.read_excel(fpath) 
    varname = df.columns
    #group = re.findall(r'\w*Group\w*', varname)
    
    #student = re.findall(r'\w*Student\w*', varname)
    
    if ana == 'all_score':
        score = re.findall(r'\w*Score\w*', str(varname))
        if score:
            vrbs =  score
            outs = descri(df,vrbs,opath,'all_score_%s' % pp)#必须加引号
            #'["yw","yy","ws","ls","wz","lz","zf"]'
            #"zf"
            #更新数据库
            post.anal_date = timezone.now()
            post.if_anal = post.if_anal+'all_score,'
            post.save() 
        else:
            outs = 'Make sure there are data columns named incloding "Score"'
    if ana == 'all_choice':
        choice = re.findall(r'\w*Choice\w*', str(varname))
        if choice:
            vrbs =  choice 
            outs = stdscore(df,vrbs,opath,'all_choice_%s' % pp)#必须加引号
            #更新数据库
            post.anal_date = timezone.now()
            post.if_anal = post.if_anal+'all_choice,'
            post.save() 
        else:
            outs = 'Make sure there are data columns named incloding "Choice"'        
    return render(request, 'analysis_finish.html', {'post': post,
                                                    'get_ana': get_ana,
                                                    'outs': outs})

def result_detail(request, pp, ana):
    get_ana = ana
    post = get_object_or_404(Upfile, pk=pp)
    opath = './upload/out/'
    des_out = str(opath) + 'des_'+str(pp)+'.xls' #路径目录必须已经存在
    std_out = str(opath) + 'std_'+str(pp)+'.xls' #路径目录必须已经存在
    score_out = str(opath) + 'all_score_'+str(pp)+'.xls' #路径目录必须已经存在
    choice_out = str(opath) + 'all_choice_'+str(pp)+'.xls' #路径目录必须已经存在
    if ana == 'des':
        outs = pd.read_excel(des_out) 
    if ana == 'std':
        outs = pd.read_excel(std_out)
    if ana == 'all_score':
        outs = pd.read_excel(score_out) 
    if ana == 'all_choice':
        outs = pd.read_excel(choice_out)
    return render(request, 'result_detail.html', {'post': post,
                                                  'get_ana': get_ana,
                                                  'outs':outs})
 
  

def descri(df,courses,outpath,outname):
    des = df.describe()
    des2 = des.T.query('index == %s' % courses)#courses的值必须加中括号和引号
    des2["差异系数"] = des2["mean"]/des2["std"]
    #输出为excel
    des2.to_excel("%s%s.xls" % (outpath,outname),"Sheet1")#路径目录必须已经存在
    return des2

def stdscore(df,course,outpath,outname):
    df2 = df[df["%s" % course] >= 0]
    df2["T分数_%s" % course] = ( df2["%s" % course] - df2["%s" % course].mean() )\
    / df2["%s" % course].std()*10+50
    subscore = df2.ix[:,["%s" % course,"T分数_%s" % course]]
    subscore = subscore.sort_values(by=["T分数_%s" % course],ascending=[True]) #must have 'subscore = '
    #输出为excel
    subscore.to_excel("%s%s.xls" % (outpath,outname),"Sheet1")#路径目录必须已经存在
    return subscore

def file_down(request,p1):
    fname = str(p1) + '.xls'
    fpath = './upload/test/'+ str(p1) + '.xls'
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

def file_download(request,pp):
    post = get_object_or_404(Upfile, pk=pp)
    fpath = './'+str( post.file_path )
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
    response['Content-Disposition'] = 'attachment; filename=%s' % fpath
    return response

def result_download(request,pp,p1):
    fpath = './upload/out/'+str( p1 )+'_'+str( pp )+'.xls'
    fname = str( p1 )+'_'+str( pp )+'.xls'
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