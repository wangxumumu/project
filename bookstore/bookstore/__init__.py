from __future__ import absolute_import, unicode_literals #实现异步发送邮件

import pymysql
pymysql.install_as_MySQLdb()

from .celery import app as celery_app #实现异步发送邮件
__all__ = ['celery_app'] #实现异步发送邮件