from __future__ import absolute_import,unicode_literals
import os
from celery import Celery

#下面的话的意思是－为celery设置默认的django模块
# set the default Django settings module for the 'celery' program.
os.environ.setdefault('DJANGO_SETTINGS_MODULE','bookstore.settings')

app = Celery('bookstore',broker='redis://127.0.0.1:6379/6')

app.config_from_object('django.conf:settings',namespace='CELERY')

#从所有注册的Django应用程序中加载任务模块
app.autodiscover_tasks()

@app.task(bind=True)
def debug_task(self):
    print('Request: {0!r}'.format(self.request))



#
# from __future__ import absolute_import, unicode_literals
# import os
# from celery import Celery
#
# # set the default Django settings module for the 'celery' program.
# os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'bookstore.settings')
#
# app = Celery('bookstore', broker='redis://127.0.0.1:6379/6')
#
# # Using a string here means the worker doesn't have to serialize
# # the configuration object to child processes.
# # - namespace='CELERY' means all celery-related configuration keys
# #   should have a `CELERY_` prefix.
# app.config_from_object('django.conf:settings', namespace='CELERY')
#
# # Load task modules from all registered Django app configs.
# app.autodiscover_tasks()
#
#
# @app.task(bind=True)
# def debug_task(self):
#     print('Request: {0!r}'.format(self.request))










