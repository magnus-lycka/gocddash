#!/usr/bin/env python3

from gocddash.analysis.data_access import get_connection

if __name__ == '__main__':
    get_connection().truncate_tables()
