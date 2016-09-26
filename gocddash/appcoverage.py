import atexit
import coverage
import os
from flask import make_response, Blueprint

MEASURE_COVERAGE = os.environ.get('COVERAGE', False)

if MEASURE_COVERAGE:
    os.makedirs('/tmp/gocddash-cover/', exist_ok=True)
    COV = coverage.Coverage(
        data_file='/tmp/gocddash-cover/coverage',
        data_suffix=True,
        branch=True,
        source=['gocddash']
    )
    COV.start()


    def stop_coverage():
        COV.stop()
    atexit.register(stop_coverage)


cover = Blueprint('coverage', __name__)


@cover.route("/")
def report_coverage():
    if MEASURE_COVERAGE:
        COV.stop()
        COV.save()
        COV.start()
        return make_response('OK', 201)
    return make_response('Not measuring coverage.', 404)

