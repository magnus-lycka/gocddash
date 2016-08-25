#!/usr/bin/env bash

python -m modulegraph -x argparse -x pandas -x psycopg2 -x json -x datetime -x datetime.datetime -x requests -x re \
       -x smtplib -x pathlib -x flask -x flask.Config -x bs4 -x bs4.BeautifulSoup -x html -x email -x email.mime.text \
       -x email.mime.text.MIMEText -x pathlib -x pathlib.Path -x collections -x collections.defaultdict -x codecs \
       -x os -x math -x functools -x xml -x xml.etree -x xml.etree.ElementTree go_cli.py -g > go_cli_deps.dot

dot -Tpng -O go_cli_deps.dot

python -m modulegraph -x argparse -x pandas -x psycopg2 -x json -x datetime -x datetime.date -x datetime.datetime \
       -x inspect  -x requests -x re -x smtplib -x pathlib -x flask -x flask.Config -x flask.redirect \
       -x flask.Blueprint -x flask.url_for -x flask.Flask -x flask.make_response -x flask.request -x flask.abort \
       -x flask.render_template -x bs4 -x bs4.BeautifulSoup -x html -x email -x email.mime.text \
       -x email.mime.text.MIMEText -x pathlib -x pathlib.Path -x collections -x collections.defaultdict \
       -x collections.OrderedDict -x codecs -x os -x math -x functools -x xml -x getpass -x os -x os.path \
       -x os.path.abspath -x sys -x bokeh   gocddash/app.py -g > gocddash_app.dot

dot -Tpng -O gocddash_app.dot
