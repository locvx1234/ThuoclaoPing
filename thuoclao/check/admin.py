from django.contrib import admin

from .models import Alert, Host, Service

admin.site.register(Alert)
admin.site.register(Host)
admin.site.register(Service)
