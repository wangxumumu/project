from django.conf.urls import url
from comments import views

urlpatterns = [
	# 像这种传参的路由，说明在视图函数里面传有参数，有几个参数这里就得写几个对应的
	url(r'^comment/(?P<books_id>\d+)/$',views.comment,name='comment'), # 评论内容
]







