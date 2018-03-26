from django.db import models
from db.base_models import BaseModel #　导入继承的BaseModel
from users.models import Passport # 导入users表中的模型
from books.models import Books # 导入模型books

# Create your models here.

class Comments(BaseModel):
	disabled = models.BooleanField(default=False,verbose_name='禁用评论')
	user = models.ForeignKey('users.Passport',verbose_name='用户ID')
	book = models.ForeignKey('books.Books',verbose_name='书籍ID')
	content = models.CharField(max_length=1000,verbose_name='评论内容')

	class Meta:
		db_table = 's_commnet_table'







