from django.conf.urls import url
from users import views

urlpatterns = [
	url(r'^register/$',views.register,name='register'),
	url(r'^register_handle/$',views.register_handle,name='register_handle'), # 用户注册处理
	url(r'^login/$',views.login,name='login'), # 显示登陆页面
	url(r'^login_check/$',views.login_check,name='login_check'), # 用户登陆校验
	url(r'^logout/$',views.logout,name='logout'), # 退出用户登陆
	url(r'^$', views.user,name='user'), # 用户中心－信息页
	url(r'^order/$',views.order,name='order'), # 用户中心－订单页
	url(r'^address/$', views.address, name='address'),  # 用户中心－地址页
]





