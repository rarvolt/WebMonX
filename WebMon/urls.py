from django.conf.urls import url, include

from . import views

urlpatterns_v1 = [
    url(r'^watches/$', views.watch_list, name='watch-list'),
    url(r'^watches/(?P<pk>[0-9]+)$', views.watch_detail, name='watch-detail'),
    url(r'^watches/(?P<pk>[0-9]+)/value$', views.watch_value_latest, name='watch-value-latest'),
    url(r'^watches/(?P<pk>[0-9]+)/value/all$', views.watch_value_list, name='watch-value-list'),

    # url(r'^users/$', views.user_list, name='user-list'),
    # url(r'^users/(?P<pk>[0-9]+)$', views.user_detail, name='user-detail'),
    # url(r'^users/(?P<pk>[0-9]+)/watches', views.user_detail_watches, name='user-detail-watches'),
]

urlpatterns = [
    url(r'^api/v1/', include(urlpatterns_v1)),
    url(r'^api-auth/', include('rest_framework.urls', namespace='rest_framework'))
]
