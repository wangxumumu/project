from django.shortcuts import render,redirect #用户提交表单时导入redirect(重导向)
import re
from users.models import Passport,Address
from django.core.urlresolvers import reverse #使用反向解析倒回到注册页面
from django.http import JsonResponse,HttpResponse
from utils.decorators import login_required #导入装饰器的模块
from order.models import OrderInfo,OrderBooks #导入订单模块
#实现发送邮件(邮箱的激活)
# itsdangerous是一个产生token的库,同步发送邮件
from itsdangerous import TimedJSONWebSignatureSerializer as Serializer # 导入序列化器
from itsdangerous import SignatureExpired
from bookstore import settings #导入settings
from django.core.mail import send_mail
from users.tasks import send_active_email #异步发送邮箱需要导入的模块



# Create your views here.

def register(request):
	#显示用户注册页面
	return render(request,'users/register.html')

#注册页面表单提交功能
def register_handle(request):
	'''进行用户注册处理'''
	#接收数据 - 获取的是页面表单提交过来的数据
	username = request.POST.get('user_name')
	password = request.POST.get('pwd')
	email = request.POST.get('email')

	#进行数据校验
	if not all([username,password,email]):
		#有数据为空返回到register.html页面
		return render(request, 'users/register.html',{'errmsg':'参数不能为空'})
	#判断邮箱是否合法
	if not re.match(r'^[a-z0-9][\w\.\-]*@[a-z0-9\-]+(\.[a-z]{2,5}){1,2}$',email):
		return render(request,'users/register.html',{'errmsg':'邮箱不合法'})


	#进行业务处理:注册，向账户系统中添加账户
	passport = Passport.objects.add_one_passport(username=username,password=password,email=email)

	#生成激活的token itsdangerous
	# serializer 序列化器
	serializer = Serializer(settings.SECRET_KEY, 3600)
	token = serializer.dumps({'confirm': passport.id})  # 返回bytes
	token = token.decode()

	#给用户的邮箱发激活邮件
	#实现同步
	# send_mail('尚硅谷书城用户激活', '', settings.EMAIL_FROM, [email],html_message='<a href="http://127.0.0.1:8000/user/active/%s/">http://127.0.0.1:8000/user/active/</a>' % token)

	send_active_email.delay(token, username, email) # 实现异步

	#注册完毕，返回注册页面
	return redirect(reverse('books:index'))

def login(request):
	#显示登陆页面
	# 获取用户名－可以从本地浏览器的缓存中获取
	username = request.COOKIES.get('username','')
	checked = ''
	context = {
		'username': username,
		'checked': checked,
	}

	return render(request,'users/login.html',context)

#进行用户登陆校验
def login_check(request):
	#1.获取数据
	username = request.POST.get('username')
	password = request.POST.get('password')
	#remember-记住用户名
	remember = request.POST.get('remember')

	#2.数据校验
	if not all([username,password]):
		#有数据为空－返回２
		return JsonResponse({'res':2})

	#3.进行处理:根据用户名和密码查找账户信息
	passport = Passport.objects.get_one_passport(username=username,password=password)
	if passport:
		#用户名密码正确
		#获取session中的url_path
		#根据反向解析
		next_url = request.session.get('url_path',reverse('books:index'))
		jres = JsonResponse({'res':1,'next_url':next_url})
		#判断是否需要记住用户
		if remember == 'true':
			#记住用户
			jres.set_cookie('username',username,max_age=7*24*3600)
		else:
			#不要记住用户
			jres.delete_cookie('username')

		#记住用户的登陆状态
		request.session['islogin'] = True
		request.session['username'] = username
		request.session['passport_id'] = passport.id
		return jres
	else:
		# 用户名或密码错误
		return JsonResponse({
			'res':0,
		})

def logout(request):
	#用户退出登陆
	#清空用户的session信息
	request.session.flush()
	#跳转到首页
	return redirect(reverse('books:index'))

@login_required
def user(request):
	#用户中心－信息页
	#从服务端获取账户的id
	passport_id = request.session.get('passport_id')
	#获取用户的基本信息
	#获取默认的地址　（字段账户的id=服务段传的账户id）
	addr = Address.objects.get_default_address(passport_id=passport_id)

	books_li = []
	context = {
		'addr':addr, #地址
		'page':'user', #用户名
		'books_li':books_li #从书的列表中取出的具体哪本书
	}

	return render(request,'users/user_center_info.html',context)


#用户中心－订单页
@login_required
def order(request):
	#查询用户的订单信息
	passport_id = request.session.get('passport_id')

	#获取订单信息
	order_li = OrderInfo.objects.filter(passport_id=passport_id)

	#遍历获取订单的商品信息
	#order -> OrderInfo实例对象
	for order in order_li:
		#根据订单id产训订单商品呢信息
		order_id = order.order_id
		order_books_li = OrderBooks.objects.filter(order_id=order_id)

		#计算商品的小计
		#order_books -> OrderBooks实例对象
		for order_books in order_books_li:
			count = order_books.count #订单书的数量
			price = order_books.price #订单书的价格
			amount = count * price #书的数量＊书的价格＝总金额
			#保存订单中每一个商品的小计
			order_books.amount = amount


		#给order对象动态增加一个属性order_books_li,保存订单中商品的信息
		order.order_books_li = order_books_li
	context = {
		'order_li': order_li,
		'page': 'order'
	}
	return render(request,'users/user_center_order.html',context)

#实现收获地址功能
@login_required
def address(request):
	#用户中心－地址页
	passport_id = request.session.get('passport_id')
	if request.method == 'GET':
		#显示地址页面
		#查询用户的默认地址
		addr = Address.objects.get_default_address(passport_id=passport_id)
		return render(request,'users/user_center_site.html',{'addr':addr,'page':'address'})

	else:
		#添加收获数据
		#1.接收数据
		recipient_name = request.POST.get('username') #收获人名字
		recipient_addr = request.POST.get('addr') #收获地址
		zip_code = request.POST.get('zip_code') #邮政编码
		recipient_phone = request.POST.get('phone') #联系方式


		#2.进行校验
		if not all([recipient_name,recipient_addr,zip_code,recipient_phone]):
			return render(request,'users/user_center_site.html',{'errmsg':'参数不能为空'})

		#3.添加收获地址
		Address.objects.add_one_address(
			passport_id=passport_id,
			recipient_name=recipient_name,
			recipient_addr=recipient_addr,
			zip_code=zip_code,
			recipient_phone=recipient_phone
		)

		#4.返回应答
		return redirect(reverse('user:address'))














































