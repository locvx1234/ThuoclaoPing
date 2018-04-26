from django.conf.urls import url
from check import views


urlpatterns = [
    url(r'^.*\.html', views.view_html, name='view_html'),

    # The home page
    url(r'^$', views.index, name='index'),

    # The config host page
    url(r'^host$', views.host, name='host'),
    url(r'^host/delete/(?P<host_id>\d+)/$', views.delete_host, name='delete_host'),
    url(r'^host/edit/(?P<host_id>\d+)/$', views.edit_host, name='edit_host'),
    url(r'^service$', views.service, name='service'),
    url(r'^service/config/(?P<service_id>\d+)/$', views.config_service, name='config_service'),
    url(r'^service/remove/(?P<service_id>\d+)/$', views.remove_service, name='remove_service'),
    url(r'^ajax/get_data/(?P<pk_host>\d+)/(?P<service_name>[-\w]+)/$', views.get_data, name='get_data')
]
