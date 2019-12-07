#coding:utf-8
from django import forms
from django.forms import ModelForm
#from captcha.fields import CaptchaField
from django.contrib.auth.models import User
from accounts.models import *
from django.forms.extras.widgets import * #如果django版本大于1.9则不需要
#from bootstrap_toolkit.widgets import BootstrapDateInput, BootstrapTextInput, BootstrapUneditableInput




GENDER_CHOICES=(
('male','男'),
('female','女')
)

BIRTH_YEAR_CHOICES = ('1995','1996','1997','1998', '1999','2000', 
    '2001', '2002','2003','2004', '2005', 
    '2006','2007','2008', '2009', '2010',
    '2011','2012','2013','2014','2015'
    )
JOIN_SCHOOL_YEAR_CHOICES = ('2014', '2015', '2016','2017','2018')

class LoginForm(forms.Form):
    username = forms.CharField(
        required=True,
        label=u"用户名",
        error_messages={'required': '请输入用户名'},
        help_text = u'如果不记得学号请问老师',
        widget=forms.TextInput(
            attrs={
                'placeholder':u"用户名、邮箱或手机号",
            }
        ),
    )    
    password = forms.CharField(
        required=True,
        label=u"密码",
        error_messages={'required': u'请输入密码'},
        widget=forms.PasswordInput(
            attrs={
                'placeholder':u"密码",
            }
        ),
    ) 
    

    def clean(self):
        
        if self.is_valid():
            cleaned_data = super(LoginForm, self).clean()


def validate_phone(value):
    if not value.isdigit():
        raise forms.ValidationError(u'%s不是电话号码' % value)
def validate_user(username):
    user = User.objects.filter(username=username)
    if user.count():
        raise forms.ValidationError(u'%s已经被注册' % username)
def validate_psw(value):
    if len(value) < 6:
        raise forms.ValidationError(u'密码长度不够' )
def validate_school(value):
    user = SchoolInfo.objects.filter(schoolname=value)
    if user.count():
        raise forms.ValidationError(u'%s已经被注册' % value)
def validate_inyear(value):
    if not value.isdigit():
        raise forms.ValidationError(u'%s不是数字格式' % value)
    elif len(value) != 8:
        raise forms.ValidationError(u'长度8位的数字' )
def validate_clarkno(value):
    if not value.isdigit():
        raise forms.ValidationError(u'%s不是数字格式' % value)
    elif len(value) < 1:
        raise forms.ValidationError(u'长度不够' )

class RegisterForm(forms.Form): 
    '''
    schcode = forms.CharField(
        required=True,validators=[validate_clarkno],
        label=u"单位代码注册口令 (*)",
        error_messages={'required': '必填'},
        widget=forms.TextInput(
            attrs={
                'placeholder':u" 必填,数字 *",
            }
        )
    )  
    '''    
    username = forms.CharField(
        required=True,validators=[validate_user],
        label=u"用户名 (*)",
        error_messages={'required': '必填'},
        widget=forms.TextInput(
            attrs={
                'placeholder':u" 用户名 *",
            }
        )
    )  
    clarkno = forms.CharField(
        required=True,validators=[validate_clarkno],
        label=u"工号 (*)",
        error_messages={'required': '必填'},
        widget=forms.TextInput(
            attrs={
                'placeholder':u" 必填,数字 *",
            }
        )
    )      
    password1 = forms.CharField(
        required=True,validators=[validate_psw],
        label=u"密码 (*)",
        error_messages={'required': u'必填,6位以上字母数字符号'},
        widget=forms.PasswordInput(
            attrs={
                'placeholder':u"密码 *6位以上 ",
            }
        ),
    )  
    password2 = forms.CharField(
        required=True,validators=[validate_psw],
        label=u"密码确认 (*)",
        error_messages={'required': u'请确保两次密码一致'},
        widget=forms.PasswordInput(
            attrs={
                'placeholder':u"密码确认 *",
            }
        ),
    )  
    
    truename = forms.CharField(
        required=True,
        label=u"真实姓名 (*)",
        error_messages={'required': u'请输入真实姓名以方便辨认'},
        widget=forms.TextInput(
            attrs={
                'placeholder':u"真实姓名 (*)",
            }
        ),
    ) 


    gender = forms.ChoiceField(
        required=True,
        label="性别(*)",
        widget=forms.Select(),
        choices=GENDER_CHOICES,
        )

    #注意django版本小于1.9时需要importSelectDateWidget
    birthday = forms.DateField(required=True,label=u"出生日期 (*)",widget=SelectDateWidget(years=BIRTH_YEAR_CHOICES,attrs={'class':'form-control rounded'}),)
    
    
    inyear = forms.CharField(
        required=True,validators=[validate_inyear],
        label=u"入职日期 (*)",
        error_messages={'required': u'请输入入职年份'},
        widget=forms.TextInput(
            attrs={
                'placeholder':u"必填,8位数字如:20170522",
            }
        ),
    ) 

    
    work = forms.CharField(
        required=False,
        label=u"职务",
        error_messages={'required': u'职务'},
        widget=forms.TextInput(
            attrs={
                'placeholder':u"职务名称",
            }
        ),
    )  
    
    email = forms.CharField(
        required=False,
        label=u"电子邮件",
        error_messages={'required': u'请输入电子邮件地址'},
        widget=forms.EmailInput(
            attrs={
                'placeholder':u"电子邮件",
            }
        ),
    )  
    phone = forms.CharField(
        required=False,validators=[validate_phone],
        label=u"电话号码",
        error_messages={'required': u'请输入电话号码,方便联系'},
        widget=forms.TextInput(
            attrs={
                'placeholder':u"电话号码",
            }
        ),
    )

    #usergroup = forms.ChoiceField(choices=USER_GROUPS,label='用户类型') 
    #不做选择,默认以学生身份注册;管理员可以修改user将用户改为教师类型
    def clean(self):
        if not self.is_valid():
            raise forms.ValidationError(u"必填项没有填写")
        elif len(self.cleaned_data['password1']) < 6 or len(self.cleaned_data['password2']) < 6:
            raise forms.ValidationError(u"密码长度不够,必须大于6位")
        elif self.cleaned_data['password1'] != self.cleaned_data['password2']:
            raise forms.ValidationError(u"两次输入的密码不一样")
        else:
            cleaned_data = super(RegisterForm, self).clean()
        return cleaned_data


class PasswordForm(forms.Form):
    oldpassword = forms.CharField(
        required=True,
        label=u"原密码",
        error_messages={'required': u'请输入原密码'},
        widget=forms.PasswordInput(
            attrs={
                'placeholder':u"原密码",
            }
        ),
    ) 
    newpassword1 = forms.CharField(
        required=True,
        label=u"新密码",
        error_messages={'required': u'请输入新密码'},
        widget=forms.PasswordInput(
            attrs={
                'placeholder':u"新密码",
            }
        ),
    )
    newpassword2 = forms.CharField(
        required=True,
        label=u"确认密码",
        error_messages={'required': u'请再次输入新密码'},
        widget=forms.PasswordInput(
            attrs={
                'placeholder':u"确认密码",
            }
        ),
    ) 
    def clean(self):
        if not self.is_valid():
            raise forms.ValidationError(u"所有项都为必填项")
        elif len(self.cleaned_data['newpassword1']) < 6 or len(self.cleaned_data['newpassword2']) < 6:
            raise forms.ValidationError(u"新密码长度不够,必须大于6位")
        elif self.cleaned_data['newpassword1'] != self.cleaned_data['newpassword2']:
            raise forms.ValidationError(u"两次输入的新密码不一样")
        else:
            cleaned_data = super(PasswordForm, self).clean()
        return cleaned_data




class ImpStuForm(forms.Form):
    stufile = forms.FileField(required=False,label=u"选择excel文件")
    def clean(self):
        if not self.is_valid():
            raise forms.ValidationError(u"必填项没有填写")
        else:
            cleaned_data = super(ImpStuForm, self).clean()
        return cleaned_data
'''
SCHOOL_TYPES = (
       ('Level_1_Sheng', '省级'),
       ('Level_2_DiShi', '地市级'),
       ('Level_3_QuXian', '区县级'),
       ('Level_4_XiaoQu', '小区级'),
)
'''
SCHOOL_TYPES = (
       ('省级', '省级'),
       ('地市级', '地市级'),
       ('区县级', '区县级'),
       ('小区级', '小区级'),
)
class AddSchForm(forms.Form):
    '''
    schooltype = forms.ChoiceField(
            choices=SCHOOL_TYPES,label='机构类型'
            )
'''
    school = forms.CharField(
        required=True,
        label=u"机构名称",
        error_messages={'required': u'请输入机构名称'},
        widget=forms.TextInput(
            attrs={
                'placeholder':u"完整的机构名称,唯一，必填",
            }
        ),
    )  
    schoolcode = forms.CharField(
        required=True,
        label=u"单位代码，注册口令",
        error_messages={'required': u'请输入单位代码'},
        widget=forms.TextInput(
            attrs={
                'placeholder':u"单位代码，用户注册时会用到,必填",
            }
        ),
    ) 
    '''
    district = forms.CharField(
        required=True,
        label=u"区县名称",
        error_messages={'required': u'请输入区县名称'},
        widget=forms.TextInput(
            attrs={
                'placeholder':u"必填",
            }
        ),
    )  
    city = forms.CharField(
        required=True,
        label=u"地市名称",
        error_messages={'required': u'请输入城市名称'},
        widget=forms.TextInput(
            attrs={
                'placeholder':u"必填",
            }
        ),
    )  
    province = forms.CharField(
        required=True,
        label=u"省份名称",
        error_messages={'required': u'请输入省份名称'},
        widget=forms.TextInput(
            attrs={
                'placeholder':u"必填",
            }
        ),
    ) 
'''
    def clean(self):
        if not self.is_valid():
            raise forms.ValidationError(u"必填项没有填写")
        else:
            cleaned_data = super(AddSchForm, self).clean()
        return cleaned_data
''' 
SCORE_TYPES=(
('plus','加分'),
('minus','减分')
)
'''
#中文
SCORE_TYPES=(
('加分','加分'),
('减分','减分')
)  
class AddScoreForm(forms.Form):
    scoretype = forms.ChoiceField(
            choices=SCORE_TYPES,label='加减分数'
            ) 
    score = forms.CharField(
        required=True,
        label=u"分值",
        error_messages={'required': u'请输入分值'},
        widget=forms.TextInput(
            attrs={
                'placeholder':u"请输入数字,必填",
            }
        ),
    )  
    employee = forms.CharField(
        required=True,
        label=u"员工工号",
        error_messages={'required': u'请输入员工工号'},
        widget=forms.TextInput(
            attrs={
                'placeholder':u"请输入员工号,唯一，必填",
            }
        ),
    ) 
    issue = forms.CharField(
        required=True,
        label=u"事件",
        error_messages={'required': u'请输入事件'},
        widget=forms.Textarea(
            attrs={
                'placeholder':u"请输入事件,必填",
            }
        ),
    ) 
    otherwords = forms.CharField(
        required=False,
        label=u"备注",
        error_messages={'required': u'请输入备注'},
        widget=forms.Textarea(
            attrs={
                'placeholder':u"备注",
            }
        ),
    ) 
    def clean(self):
        if not self.is_valid():
            raise forms.ValidationError(u"必填项没有填写")
        else:
            cleaned_data = super(AddScoreForm, self).clean()
        return cleaned_data
'''    
class OftenIssueForm(ModelForm):
    #file_format = forms.ChoiceField(choices=FILE_FORMAT,label='文件格式',)
    #sex = forms.ChoiceField(widget=forms.RadioSelect,choices=SEX_CHOICES,label="性别")
    #birthday = forms.DateField(widget=SelectDateWidget(years=BIRTH_YEAR_CHOICES))#注意django版本小于1.9时需要import
    class Meta:
        model = OfenIssue #从model而来s
        fields = ( 
        'issue',
        'scoretype',
        'score',
        'check',
        'otherwords',
        ) #'file_format','if_often','if_homepage','tips','labels','qnname',
    def clean(self):
        if not self.is_valid():
            raise forms.ValidationError(u"必填项没有填写")
        else:
            cleaned_data = super(OftenIssueForm, self).clean()
        return cleaned_data
'''
class OftenIssueForm(forms.Form):
    scoretype = forms.ChoiceField(
            choices=SCORE_TYPES,label='加减分数'
            ) 
    score = forms.CharField(
        required=True,
        label=u"分值",
        error_messages={'required': u'请输入分值'},
        widget=forms.TextInput(
            attrs={
                'placeholder':u"请输入数字,必填",
            }
        ),
    ) 
    issue = forms.CharField(
        required=True,
        label=u"事件",
        error_messages={'required': u'请输入事件'},
        widget=forms.TextInput(
            attrs={
                'placeholder':u"请输入事件,必填",
            }
        ),
    ) 
    check = forms.CharField(
        required=True,
        label=u"是否审核",
        error_messages={'required': u'请输入'},
        widget=forms.TextInput(
            attrs={
                'placeholder':u"是否需要审核",
            }
        ),
    ) 
    otherwords = forms.CharField(
        required=False,
        label=u"备注",
        error_messages={'required': u'请输入备注'},
        widget=forms.Textarea(
            attrs={
                'placeholder':u"备注",
            }
        ),
    ) 
    def clean(self):
        if not self.is_valid():
            raise forms.ValidationError(u"必填项没有填写")
        else:
            cleaned_data = super(OftenIssueForm, self).clean()
        return cleaned_data