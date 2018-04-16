from django.conf.urls import url
from . import views

urlpatterns = [
    url(r'^.*\.html', views.view_html, name='view_html'),

    # The home page
    url(r'^$', views.index, name='index'),
    # The config host page
    url(r'^host$', views.host, name='host'),
    url(r'^service$', views.service, name='service'),

]