from werkzeug.contrib.profiler import ProfilerMiddleware
from app import app

pstat_dir = '/home/magnusl/work/gocddash/gocddash/pstat'
app.config['PROFILE'] = True
app.wsgi_app = ProfilerMiddleware(app.wsgi_app, restrictions=[30])
# app.wsgi_app = ProfilerMiddleware(app.wsgi_app, profile_dir=pstat_dir)
app.run(debug=True)
