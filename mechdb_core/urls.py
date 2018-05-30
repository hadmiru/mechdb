from django.conf.urls import url
from . import views

urlpatterns = [
    url(r'^$', views.index_page, name='index_page'),
    # === контейнеры ===
    url('map/', views.containers_map, name='containes_map'),
    url(r'^place/(?P<pk>\d+)/$', views.container_detail, name='container_detail'),
    url(r'^place/new/$', views.container_new, name='container_new'),
    url(r'^place/(?P<pk>\d+)/edit/$', views.container_edit, name='container_edit'),
    # === оборудование ===
    url(r'^equipment/list/$', views.equipment_list, name='equipment_list'),
    url(r'^equipment/(?P<pk>\d+)/$', views.equipment_detail, name='equipment_detail'),
    # === типоразмеры ===
    url(r'^model/list/$', views.sizename_list, name='sizename_list'),
    url(r'^model/(?P<pk>\d+)/$', views.sizename_detail, name='sizename_detail'),
]
