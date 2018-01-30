from django.db import models
from db.base_models import BaseModel
from order.enums import *
# Create your models here.

#订单商品模型类
class OrderBooks(BaseModel):

	order = models.ForeignKey('OrderInfo',verbose_name='所属订单')
	books = models.ForeignKey('books.Books',verbose_name='订单商品')
	#IntegerField -> 整数字段
	count = models.IntegerField(default=1,verbose_name='商品数量')
	#DecimalField -> 固定精度的十进制的字段
	#max_digits=10 ->数字允许的最大为10(包括小位数)
	#decimal_places=2 ->小数位最大保留２位
	price = models.DecimalField(max_digits=10,decimal_places=2,verbose_name='商品价格')

	class Meta:
		db_table = 's_order_books'


#订单信息表
class OrderInfo(BaseModel):
	order_id = models.CharField(max_length=64,primary_key=True,verbose_name='订单编号')
	passport = models.ForeignKey('users.Passport',verbose_name='下单账户')
	addr = models.ForeignKey('users.Address',verbose_name='收货地址')
	#IntegerField->整数字段，从-2147483648到2147483647 范围内的值是合法的，默认为１
	total_count = models.IntegerField(default=1,verbose_name='商品总数')
	#DecimalField　->固定精度的十进制的字段，最大位数保留10位(包括小位数)，小数的最大位数保留２位
	total_price = models.DecimalField(max_digits=10,decimal_places=2,verbose_name='商品总价')
	transit_price = models.DecimalField(max_digits=10,decimal_places=2,verbose_name='订单运费')
	#SmallIntegerField 短整形字段，范围：-32768到32767
	#choices=PAY_METHOD_CHOICES 支付方式的选择，默认为１，现金支付
	pay_method = models.SmallIntegerField(choices=PAY_METHOD_CHOICES,default=1,verbose_name='支付方式')
	#choices=ORDER_STATUS_CHOICES 订单状态的选择，默认为１，待付款
	status = models.SmallIntegerField(choices=ORDER_STATUS_CHOICES,default=1,verbose_name='订单状态')
	#unique=True - 唯一的
	#null=True - 数据库写入的字段数据可以为空
	#blank是表单数据输入验证范畴的
	#blank=True - 提交表单时表单的验证允许输入一个空值，为false时，该字段就得必填
	trade_id = models.CharField(max_length=100,unique=True,null=True,blank=True,verbose_name='支付编号')

	class Meta:
		db_table = 's_order_info'#更改数据库的表明为指定的名字











