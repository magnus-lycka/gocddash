#!/usr/bin/env python3
# coding:utf-8

from distutils.core import setup

install_requires = []
with open('requirements.txt') as req_file:
    for row in req_file:
        req = row.strip()
        if req:
            install_requires.append(req)

if __name__ == '__main__':
    setup(
        name='gocddash',
        version='2.0.1',
        description='A status dashboard for Go.CD.',
        author='Magnus Lyckå, Emily Bache',
        author_email='magnus@thinkware.se, emily.bache@pagero.com',
        license='MIT',
        install_requires=install_requires,
        url='https://github.com/magnus-lycka/gocddash',
        classifiers=[
            "Programming Language :: Python :: 3.4",
            "License :: OSI Approved :: MIT License",
            "Operating System :: POSIX :: Linux",
            "Development Status :: 4 - Beta",
            "Intended Audience :: Developers",
            "Topic :: Software Development :: Build Tools",
            "Environment :: Web Environment",
        ],
        keywords='continuous deployment integration build automation go.cd monitoring dashboard',
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
        data_files=[('', ['requirements.txt'])],
        scripts=[
            'gocddash/gocddash_app.py',
            'gocddash/gocddash_profiler.py',
            'gocddash_sync.py',
            'gocddash_cli.py',
            'gocddash_truncate.py'],
    )
