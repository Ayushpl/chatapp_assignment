
import multiprocessing

bind = '127.0.0.1:8001'
workers = multiprocessing.cpu_count() * 2 + 1
secure_scheme_headers = {'X-FORWARDED-PROTO': 'https'}
reload = True
errorlog = '-'
accesslog = '-'
loglevel = 'info'
# timeout = 300
access_log_format = '%({X-Forwarded-For}i)s %(l)s %(u)s %(t)s "%(r)s" %(s)s %(b)s "%(f)s" "%(a)s"'
worker_class = 'uvicorn.workers.UvicornWorker'