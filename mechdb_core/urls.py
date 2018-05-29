from django.conf.urls import url
from . import views

urlpatterns = [
    url(r'^$', views.index_page, name='index_page'),
    url('map/', views.containers_map, name='containes_map'),
    url(r'^place/(?P<pk>\d+)/$', views.container_detail, name='container_detail'),
    url(r'^place/new/$', views.container_new, name='container_new'),
]
