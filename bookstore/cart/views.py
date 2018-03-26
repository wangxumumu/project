from django.shortcuts import render
from django.http import JsonResponse
from books.models import Books
from django_redis import get_redis_connection
from utils.decorators import login_required
# Create your views here.

#向购物车中添加商品的功能
#前端发过来的数据:商品id,商品数目,books_id  books_count
#涉及到数据的修改，使用post方式
def cart_add(request):
	#向购物车中添加数据
	#判断用户是否登陆
	#has_key()方法->函数用于判断键是否存在于字典中，如果键在字典dict里返回true，否则返回false。
	if not request.session.has_key('islogin'):
		return JsonResponse({'res':0,'errmsg':'请先登录'})

	#接收数据
	#接收请求获取书的id(POST加密的)
	books_id = request.POST.get('books_id')
	#接收请求获取书的数量
	books_count = request.POST.get('books_count')

	#进行数据校验
	if not all([books_id,books_count]):
		return JsonResponse({'res':1,'errmsg':'数据不完整'})

	books = Books.objects.get_books_by_id(books_id=books_id)
	if books is None:
		#商品不存在
		return JsonResponse({'res':2,'errmsg':'商品不存在'})

	try:
		count = int(books_count)
	except Exception as e:
		#商品数目不合法
		return JsonResponse({'res':3,'errmsg':'商品数量必须为数字'})

	#添加商品到购物车
	#每个用户的购物车记录用一条hash数据保存,格式:cart_用户id, 商品id，商品数量
	conn = get_redis_connection('default')
	cart_key = 'cart_%d' % request.session.get('passport_id')

	res = conn.hget(cart_key,books_id)
	if res is None:
		#如果用户的购物车中没有添加过该商品，则添加数据
		res = count
	else:
		#如果用户的购物车中已经添加过该商品，则累计商品数目
		res = int(res) + count

	#判断商品的库存
	if res > books.stock:
		#库存不足
		return JsonResponse({'res':4,'errmsg':'商品库存不足'})
	else:
		conn.hset(cart_key,books_id,res)

	#返回结果
	return JsonResponse({'res':5})


def cart_count(request):
	#获取用户购物车中商品的数目
	#判断用户是否登陆
	if not request.session.has_key('islogin'):
		return JsonResponse({'res': 0})

	#计算用户购物车商品的数量
	conn = get_redis_connection('default')
	cart_key = 'cart_%d' % request.session.get('passport_id')

	#res = conn.hlen(cart_key) 显示商品的条目数
	res = 0
	#hvals(cart_key)-得到cart_key所有的属性值
	res_list = conn.hvals(cart_key)

	for i in res_list:
		res += int(i)
	#返回结果
	return JsonResponse({'res':res})

@login_required #使用这个装饰器是判断是否登陆
def cart_show(request):
	#显示用户购物车页面
	passport_id = request.session.get('passport_id')
	#获取用户购物车的记录
	conn = get_redis_connection('default')
	cart_key = 'cart_%d' % passport_id
	res_dict = conn.hgetall(cart_key)

	books_li = []
	#保存所有的商品的总数
	total_count = 0
	#保存所有商品的总价格
	total_price = 0

	#遍历res_dict获取商品的数据
	for id,count in res_dict.items():
		#根据id获取商品的信息
		books = Books.objects.get_books_by_id(books_id=id)
		#保存商品的数目
		books.count = count
		#保存商品的小计
		books.amount = int(count) * books.price
		books_li.append(books)#往书的列表中添加书

		total_count += int(count)
		total_price += int(count) * books.price

	#定义模板上下文
	context = {
		'books_li': books_li,
		'total_count': total_count,
		'total_price': total_price,
	}

	return render(request,'cart/cart.html',context)


#购物车中删除商品的功能
def cart_del(request):
	#删除用户购物车中商品的信息
	#判断用户是否登陆
	if not request.session.has_key('islogin'):
		return JsonResponse({'res':0,'errmsg':'请先登录'})

	#接收数据
	books_id = request.POST.get('books_id')

	#校验商品是否存放
	if not all([books_id]):
		return JsonResponse({'res':1,'errmsg':'数据不完整'})

	books = Books.objects.get_books_by_id(books_id=books_id)
	if books is None:
		return JsonResponse({'res':2,'errmsg':'商品不存在'})

	#删除购物车商品信息
	conn = get_redis_connection('default')
	cart_key = 'cart_%d' % request.session.get('passport_id')
	conn.hdel(cart_key,books_id)


	#返回信息
	return JsonResponse({'res':3})

#此函数实现购物车页面编辑商品数量的功能
def cart_update(request):

	#更新购物车商品数目
	#判断用户是否登陆
	if not request.session.has_key('islogin'):
		return JsonResponse({'res':0,'errmsg':'请先登陆'})

	#接收数据
	books_id = request.POST.get('books_id')
	books_count = request.POST.get('books_count')

	#数据的校验
	#判断的书的id和书的数量是否缺少，二者不能缺少一个，如果缺少一个条件不成立
	if not all([books_id,books_count]):
		return JsonResponse({'res':1,'errmsg':'数据不完整'})

	books = Books.objects.get_books_by_id(books_id=books_id)
	if books is None:
		return JsonResponse({'res':2,'errmsg':'商品不存在'})

	try:
		books_count = int(books_count)#因为接受到的数据不一定是数字类型的，所以要强转一下
	except Exception as e:
		return JsonResponse({'res':3,'errmsg':'商品数目必须为数字'})

	#更新操作
	#连接redis
	conn = get_redis_connection('default')
	#根据用户的id得到cart_key，用来区分每一个用户的购物车
	cart_key = 'cart_%d' % request.session.get('passport_id')

	#判断商品库存
	if books_count > books.stock:#判读书的数量是否大于书的库存
		return JsonResponse({'res':4,'errmsg':'商品库存不足'})

	#hset- 设置属性值
	conn.hset(cart_key,books_id,books_count)

	return JsonResponse({'res':5})#更新成功























