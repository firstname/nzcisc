from django.contrib import admin

# Register your models here.
"""用户模块扩展"""

from accounts.models import User     
admin.site.register(User)
"""用户模块扩展"""