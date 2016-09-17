from django.conf.urls import url
from . import views

urlpatterns= [
    url(r'^$', views.index, name= 'index'),
    url(r'^reg/$', views.register, name= 'register'),
    url(r'^login/(\d+)/$',views.login, name= 'login'),
    url(r'^content/$',views.content, name='content'),
    url(r'^dashboard/$',views.dashboard, name= 'dashboard'),
    url(r'^get_restaurant/$', views.get_restaurant, name='get_restaurant'),
    url(r'^menu/$', views.menu, name = 'menu'),
    url(r'^curr_order/$',views.curr_order, name ='curr_order'),
    url(r'^get_order/$',views.getOrder, name='getOrder'),
    url(r'^rgraph/$', views.rgraph, name='rgraph'),
    url(r'^is_ready/$',views.isReady, name='is_ready'),
    url(r'^thank_you/$',views.thankYou, name='thank_you'),
    url(r'^complete/$',views.complete, name='complete'),
    url(r'^recommendation/$',views.recommendation, name='recommendation'),
    url(r'^table/$', views.table, name='table'),
]
#    url(r'^logout/$', views.logout, name='logout'),