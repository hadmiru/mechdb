from django.conf.urls import url
from . import views
from django.contrib.auth.views import password_reset, password_reset_done, password_reset_complete, password_reset_confirm

urlpatterns = [

    url(r'^user/password/reset/$', password_reset,
        {'post_reset_redirect' : '/user/password/reset/done/'},
        name="password_reset"),
    url(r'^user/password/reset/done/$',
        password_reset_done,
        name='password_reset_done'),
    url(r'^user/password/done/$',
        password_reset_complete,
        name='password_reset_complete'),
    url(r'^reset/(?P<uidb64>[0-9A-Za-z_\-]+)/(?P<token>[0-9A-Za-z]{1,13}-[0-9A-Za-z]{1,20})/$',
        password_reset_confirm,
        name='password_reset_confirm'),
    url(r'^login/$', views.signin, name='signin'),
    url(r'^logout/$', views.logout_view, name='logout_view'),
    url(r'^signup/$', views.signup, name='signup'),
    url(r'^guide/$', views.guide, name='guide'),
    url(r'^$', views.index_page, name='index_page'),
    # === контейнеры ===
    url(r'^map/', views.containers_map, name='containers_map'),
    url(r'^place/(?P<pk>\d+)/$', views.container_detail, name='container_detail'),
    url(r'^place/new/$', views.container_new, name='container_new'),
    url(r'^place/(?P<pk>\d+)/edit/$', views.container_edit, name='container_edit'),
    url(r'^place/(?P<pk>\d+)/remove/$', views.container_remove, name='container_remove'),
    # === оборудование ===
    url(r'^equipment/list/$', views.equipment_list, name='equipment_list'),
    url(r'^equipment/(?P<pk>\d+)/$', views.equipment_detail, name='equipment_detail'),
    url(r'^equipment/new/$', views.equipment_new, name='equipment_new'),
    url(r'^equipment/(?P<pk>\d+)/edit/$', views.equipment_edit, name='equipment_edit'),
    url(r'^equipment/(?P<pk>\d+)/remove/$', views.equipment_remove, name='equipment_remove'),
    # === типоразмеры ===
    url(r'^model/list/$', views.sizename_list, name='sizename_list'),
    url(r'^model/(?P<pk>\d+)/$', views.sizename_detail, name='sizename_detail'),
    url(r'^model/new/$', views.sizename_new, name='sizename_new'),
    url(r'^model/(?P<pk>\d+)/edit/$', views.sizename_edit, name='sizename_edit'),
    url(r'^model/(?P<pk>\d+)/remove/$', views.sizename_remove, name='sizename_remove'),
    # === action ===
    url(r'^action/all/$', views.action_list, name='action_list'),
    url(r'^action/(?P<pk>\d+)/$', views.action_detail, name='action_detail'),
    url(r'^action/new/$', views.action_new, name='action_new'),
    url(r'^action/(?P<pk>\d+)/edit/$', views.action_edit, name='action_edit'),
    url(r'^action/(?P<pk>\d+)/remove/$', views.action_remove, name='action_remove'),
]
