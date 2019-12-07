from django.conf.urls import include, url
from django.contrib import admin

urlpatterns = [
    # Examples:
    # url(r'^$', 'upup.views.home', name='home'),
    # url(r'^blog/', include('blog.urls')),
    url(r'^$', 'up.views.home'),
    url(r'^admin/', include(admin.site.urls)),
    url(r'^up/', 'up.views.register'),
    url(r'^list/','up.views.post_list',name='post_list'),
    url(r'^delete/(?P<pp>[0-9]+)/$', 'up.views.post_delete', name='dele_post'),
    url(r'^pre_anal/(?P<pp>[0-9]+)/$', 'up.views.pre_analysis', name='pre_analysis'),
    url(r'^anal/(?P<pp>[0-9]+)/(?P<course>\w+)/(?P<ana>\w+)/$', 'up.views.analysis', name='analysis'),
    url(r'^anal/(?P<pp>[0-9]+)/(?P<ana>\w+)/$', 'up.views.auto_analysis', name='auto_analysis'),
    url(r'^result/(?P<pp>[0-9]+)/(?P<ana>\w+)/$', 'up.views.result_detail', name='result_de'),
    url(r'^down/(?P<p1>\w+)/$', 'up.views.file_down', name='down'),
    url(r'^download/(?P<pp>[0-9]+)/$', 'up.views.file_download', name='down_file'),
    url(r'^load/(?P<pp>[0-9]+)/(?P<p1>\w+)/$', 'up.views.result_download', name='down_result'),
    #url(r'^split/(?P<pp>[0-9]+)/$', 'up.views.file_split', name='split_file'),
    url(r'^choose/(?P<pp>[0-9]+)/(?P<ana>\w+)/$',  'up.views.choose_var', name='choose_var'),
    url(r'^view/(?P<pp>[0-9]+)/(?P<p1>\w+)/$', 'up.views.vars_detail', name='vars_de'),
]

