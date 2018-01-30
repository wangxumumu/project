from django.shortcuts import redirect #重定向
from django.http import HttpResponse #http响应
from django.core.urlresolvers import reverse #反向解析


#用户中心必须登陆以后可以使用的功能函数
def login_required(view_func):
	#登陆判断装饰器
	def wrapper(request,*view_args,**view_kwargs):
		if request.session.has_key('islogin'):
			#用户已登陆
			return view_func(request,*view_args,**view_kwargs)
		else:
			#跳转到登陆页面
			return redirect(reverse('user:login'))
	return wrapper





