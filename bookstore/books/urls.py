from django.conf.urls import url
from books import views

urlpatterns = [
    url(r'^index/$', views.index, name='index'),#用户模块
    url(r'^books/(?P<books_id>\d+)/$',views.detail,name='detail'),#详情页
    url(r'^list/(?P<type_id>\d+)/(?P<page>\d+)/$',views.list,name='list'),#列表页
]