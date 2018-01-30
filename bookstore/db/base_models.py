#导入(继承)django.db的models
from django.db import models

class BaseModel(models.Model):
	#模型抽象基类
	#auto_now_add-是添加时的时间，更新对象时不会有变动
	create_time = models.DateTimeField(auto_now_add=True,verbose_name='创建时间')
	#auto_now-无论是你添加还是修改对象，时间为添加或者修改时的时间
	update_time = models.DateTimeField(auto_now=True,verbose_name='修改时间')
	is_delete = models.BooleanField(default=False,verbose_name='删除标记')

	class Meta:
		abstract = True












