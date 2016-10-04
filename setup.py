#!/usr/bin/env python3
# coding:utf-8

from distutils.core import setup


if __name__ == '__main__':
    setup(
        name='gocddash',
        version='2.0',
        description='A status dashboard for GoCD',
        author='Magnus Lyckå, Emily Bache',
        author_email='magnus@thinkware.se, emily.bache@pagero.com',
        url='https://github.com/magnus-lycka/gocd-dashboard',
        package_dir={'gocddash': 'gocddash'},
        packages=[
            'gocddash',
            'gocddash.analysis',
            'gocddash.console_parsers',
            'gocddash.dashboard',
            'gocddash.util',
        ],
        package_data={
            'gocddash': [
                'templates/*.html',
                'static/*.js',
                'static/*.css',
                'database/*.sql'
            ],
        },
        scripts=[
            'gocddash/gocddash_app.py',
            'gocddash/gocddash_profiler.py',
            'gocddash_sync.py',
            'gocddash_cli.py',
            'gocddash_truncate.py'],
    )
