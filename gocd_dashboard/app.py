from flask import Flask, render_template, request
import cctray_source
import parse_cctray


app = Flask(__name__)


@app.template_filter('bootstrap_status')
def bootstrap_status(cctray_status):
    mapping = {
        'Failure': 'danger',
        'Building after Failure': 'warning',
        'Building after Success': 'info',
        'Success': 'success',
    }
    return mapping.get(cctray_status, 'default')


#@app.before_first_request()
#def setup():
#    pass



@app.route("/", methods=['GET'])
def dashboard():
    which = request.args.get('which', 'all')
    plgroups = request.args.get('plgroups', '')
    xml = cctray_source.get_cctray_source('/Users/magnusl/Downloads/cctray.xml').xml
    #xml = cctray_source.get_cctray_source('http://go/go/cctray.xml').xml
    project = parse_cctray.Projects(xml)
    return render_template('index.html', project=project, plgroups=plgroups, which=which, cols=3)


@app.route("/select", methods=['GET', 'POST'])
def select():
    blob = ''
    if request.method == 'POST':
        blob += 'environ("wsgi.input")=' + request.environ['wsgi.input'].read()
        for attr in (''):
            blob += '\n' + attr + ':' + str(getattr(request, attr))
    blob += request.method
    import datetime
    return render_template('select.html', ts=datetime.datetime.now(), blob=blob, pipelinegroups=[
        ('checked', 'Knatte'),
        ('', 'Fnatte'),
        ('checked', 'Tjatte')])


if __name__ == "__main__":
    app.run()
