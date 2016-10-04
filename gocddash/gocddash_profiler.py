#!/usr/bin/env python3
from werkzeug.contrib.profiler import ProfilerMiddleware
from gocddash.app import app, parse_args
import getpass

pstat_dir = '/home/magnusl/work/gocddash/gocddash/pstat'
app.config['PROFILE'] = True
app.wsgi_app = ProfilerMiddleware(app.wsgi_app, restrictions=[30])
# app.wsgi_app = ProfilerMiddleware(app.wsgi_app, profile_dir=pstat_dir)

if __name__ == '__main__':
    parse_args()
    if 'GO_SERVER_URL' not in app.config:
        app.config['GO_SERVER_URL'] = input('go-server url: ')
    if 'GO_SERVER_USER' not in app.config:
        app.config['GO_SERVER_USER'] = input('go-user: ')
    if 'GO_SERVER_PASSWD' not in app.config:
        app.config['GO_SERVER_PASSWD'] = getpass.getpass()

    app.run(port=app.config['BIND_PORT'], debug=True)
