#!/usr/bin/env python3

from gocddash.analysis.data_access import get_connection, create_connection

if __name__ == '__main__':
    conn = create_connection()
    get_connection().truncate_tables()