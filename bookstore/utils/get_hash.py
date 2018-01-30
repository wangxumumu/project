from hashlib import sha1

#此函数用来避免存储文明密码的
def get_hash(str):
	# 取一个字符串的hash值
	sh = sha1()
	sh.update(str.encode('utf-8'))
	return sh.hexdigest()

