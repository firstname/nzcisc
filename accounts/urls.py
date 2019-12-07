from django.conf.urls import include, url


urlpatterns = [
    # Examples:
    # url(r'^$', 'loginproject.views.home', name='home'),
    # url(r'^blog/', include('blog.urls')),
    
    url(r'login/$', 'accounts.views.login', name='login'),
    url(r'sel_city/$', 'accounts.views.sel_city', name='sel_city'),

    url(r'signup/$', 'accounts.views.signup', name='signup'),
    url(r'register/$', 'accounts.views.register', name='register'),
    url(r'teacherreg/$', 'accounts.views.teacherreg', name='teacherreg'),
    url(r'logout/$', 'accounts.views.logout', name='logout'),
    url(r'userinfo/$', 'accounts.views.userinfo', name='userinfo'),
    url(r'changepassword/$', 'accounts.views.changepassword', name='changepassword'),
    
    url(r'userlistall/$', 'accounts.views.userlistall', name='userlistall'),
    url(r'userdeleteall/$', 'accounts.views.userdeleteall', name='userdeleteall'),
    url(r'userdelete/(?P<pp>[0-9]+)/$', 'accounts.views.userdelete', name='userdelete'),    
    url(r'userlistsch/(?P<schid>[0-9]+)/$', 'accounts.views.userlistsch', name='userlistsch'),
    
    #url(r'adduser/(?P<schcode>[0-9]+)$', 'accounts.views.adduser', name='adduser'),    
    url(r'addusersch/(?P<schid>[0-9]+)$', 'accounts.views.addusersch', name='addusersch'),
    #url(r'addtea/$', 'accounts.views.addtea', name='addtea'),
    #url(r'tealist/$', 'accounts.views.tealist', name='tealist'),
    #url(r'stulist/$', 'accounts.views.stulist', name='stulist'),
    url(r'impuser/(?P<schid>[0-9]+)$', 'accounts.views.impuser', name='impuser'),
    #url(r'studelete/(?P<pp>[0-9]+)/$', 'accounts.views.studelete', name='studelete'),    
    url(r'searchuser/$', 'accounts.views.searchuser', name='searchuser'),
    
    url(r'download/(?P<pp>[A-Za-z]+)/$', 'accounts.views.downtemplate', name='downtemplate'),
    
    url(r'schlist/$', 'accounts.views.schlist', name='schlist'),      
    url(r'schview/(?P<pp>[0-9]+)/$', 'accounts.views.schview', name='schview'),
    url(r'schdelete/(?P<pp>[0-9]+)/$', 'accounts.views.schdelete', name='schdelete'),
    url(r'schdeleteall/$', 'accounts.views.schdeleteall', name='schdeleteall'),
    url(r'addsch/(?P<schid>[0-9]+)$', 'accounts.views.addsch', name='addsch'),
    url(r'addfirstsch/$', 'accounts.views.addfirstsch', name='addfirstsch'),#
    url(r'impsch/$', 'accounts.views.impsch', name='impsch'),
    #url(r'createadmin/(?P<pp>[0-9]+)/$', 'accounts.views.createadmin', name='createadmin'),
    url(r'chooseadmin/(?P<pp>[0-9]+)/$', 'accounts.views.chooseadmin', name='chooseadmin'),


    url(r'addscore/$', 'accounts.views.addscore', name='addscore'),
    url(r'scorelist/$', 'accounts.views.scorelist', name='scorelist'),
    url(r'editissue/$', 'accounts.views.editissue', name='editissue'),


    url(r'mine/(?P<theuserid>[A-Za-z0-9]+)/$', 'accounts.views.mine', name='mine'),
]
