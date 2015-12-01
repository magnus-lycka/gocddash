import sqlite3

conn = sqlite3.connect('gocdmon.sqlite')
for table in [
    "JOBQHIST",
    "AGENTS",
    "JOBS",
    "JOB_STATE_CHANGES",
]:
    print "-" * 80
    print " TABLE:", table
    print "-" * 80
    for row in conn.execute('SELECT * FROM %s ORDER BY 1, 2, 3' % table):
        fmt = " | ".join(["%-30s" for x in range(len(row))])
        print fmt % row
conn.close()
