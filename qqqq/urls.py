from django.conf.urls import include, url
from django.contrib import admin

urlpatterns = [
    # Examples:
    # url(r'^$', 'qqqq.views.home', name='home'),
    # url(r'^blog/', include('blog.urls')),

    #url(r'^$', 'qqqq.views.home', name='home'),
    url(r'^$','accounts.views.homepage', name='homepage'),
    url(r'^help/','accounts.views.help', name='help'),
    url(r'^admin/', include(admin.site.urls)),
    url(r'^accounts/', include('accounts.urls')),
 
]
