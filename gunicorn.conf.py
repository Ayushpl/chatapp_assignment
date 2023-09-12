import multiprocessing

bind = '127.0.0.1:8000'
workers = multiprocessing.cpu_count() * 2 + 1
secure_scheme_headers = {'X-FORWARDED-PROTO': 'https'}
reload = True
errorlog = '-'
accesslog = '-'
loglevel = 'debug'
timeout = 300