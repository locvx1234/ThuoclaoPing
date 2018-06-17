from django.conf.urls import url
from check import views


urlpatterns = [
    url(r'^.*\.html', views.view_html, name='view_html'),

    # The home page
    url(r'^$', views.index, name='index'),

    # The config host page
    url(r'^host/(?P<service_name>[-\w]+)/$', views.host, name='host'),
    url(r'^host/(?P<service_name>[-\w]+)/delete/(?P<host_id>\d+)/$', views.delete_host, name='delete_host'),
    url(r'^host/(?P<service_name>[-\w]+)/delete_group/(?P<group_id>\d+)/$', views.delete_group, name='delete_group'),
    url(r'^host/(?P<service_name>[-\w]+)/edit/(?P<host_id>\d+)/$', views.edit_host, name='edit_host'),
    url(r'^host/(?P<service_name>[-\w]+)/edit_group/(?P<group_id>\d+)/$', views.edit_group, name='edit_group'),
    url(r'^ajax/get_data/(?P<pk_host>\d+)/(?P<service_name>[-\w]+)/(?P<query_time>\d+)/$', views.get_data, name='get_data'),
    url(r'^ajax/total_parameter/$', views.total_parameter, name='total_parameter'),
    url(r'^alert$', views.alert, name='alert'),
]
