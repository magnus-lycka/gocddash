#!/usr/bin/env bash
ls *.py | xargs -n 1 coverage run -a --branch --source=gocddash
