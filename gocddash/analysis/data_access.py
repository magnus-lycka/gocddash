import psycopg2


class SQLConnection:
    def __init__(self, db_port):
        self.conn = None
        self.db_port = db_port

    def connection(self):
        if not self.conn:
            conn_string = "host='dev.localhost' dbname='go-analysis' user='analysisappluser' password='analysisappluser' port='{}'".format(self.db_port)
            conn = psycopg2.connect(conn_string)
            conn.autocommit = True
            self.conn = conn.cursor()
            return self.conn
        else:
            return self.conn

    def insert_pipeline(self, id, stage_count, name, counter, trigger_message):
        self.connection().execute(
            """UPDATE pipeline SET stagecount=%s, pipelinename=%s, counter=%s, triggermessage=%s WHERE id=%s""",
            (stage_count, name, counter, trigger_message, id))
        self.connection().execute(
            """INSERT INTO pipeline(id, stagecount, pipelinename, counter, triggermessage) SELECT %s, %s, %s, %s, %s WHERE NOT EXISTS (SELECT 1 FROM pipeline WHERE id=%s);""",
            (id, stage_count, name, counter, trigger_message, id))

    def insert_stage(self, id, approved_by, pipeline_counter, pipeline_name, stage_index, result, scheduled_date, agent_uuid,
                     stage_name):
        self.connection().execute(
            """UPDATE stage SET approvedby=%s, pipelinecounter=%s, pipelinename=%s, stageindex=%s, result=%s, scheduleddate=%s, agentuuid=%s, stagename=%s WHERE id=%s;""",
            (approved_by, pipeline_counter, pipeline_name, stage_index, result, scheduled_date, agent_uuid, stage_name,
             id))
        self.connection().execute(
            """INSERT INTO stage(id, approvedby, pipelinecounter, pipelinename, stageindex, result, scheduleddate, agentuuid, stagename) SELECT %s, %s, %s, %s, %s, %s, %s, %s, %s WHERE NOT EXISTS (SELECT 1 FROM stage WHERE id=%s);""",
            (id, approved_by, pipeline_counter, pipeline_name, stage_index, result, scheduled_date, agent_uuid,
             stage_name,
             id))

    def insert_agent(self, id, agent_name):
        self.connection().execute("""INSERT INTO agent(id, agentname) VALUES (%s, %s);""", (id, agent_name))

    def insert_texttest_failure(self, stageid, testindex, failuretype, documentname):
        self.connection().execute(
            """INSERT INTO texttestfailure(stageid, testindex, failuretype, documentname) VALUES (%s, %s, %s, %s);""",
            (stageid, testindex, failuretype, documentname))

    def insert_failure_information(self, stageid, failurestage):
        self.connection().execute("""INSERT INTO failureinformation(stageid, failurestage) VALUES (%s, %s);""",
                                (stageid, failurestage))

    def insert_junit_failure_information(self, stageid, failure_type, failure_test):
        self.connection().execute("""INSERT INTO junitfailure(stageid, failuretype, failuretest) VALUES (%s, %s, %s);""",
                                (stageid, failure_type, failure_test))

    def get_highest_pipeline_count(self, pipeline_name):
        self.connection().execute("""SELECT COALESCE(max(counter), 0) FROM pipeline WHERE pipelinename = %s""",
                                (pipeline_name,))
        return self.connection().fetchone()[0]

    def get_new_agents(self):
        self.connection().execute(
            """SELECT DISTINCT agentuuid FROM stage WHERE agentuuid IS NOT NULL EXCEPT SELECT id FROM agent""")
        return map(lambda x: x[0], self.connection().fetchall())

    def is_failure_downloaded(self, stage_id):
        self.connection().execute("""SELECT * FROM failureinformation WHERE stageid=%s ;""", (stage_id,))
        return self.connection().fetchone()

    def get_failure_statistics(self, pipeline_name, months_back=1):
        self.connection().execute(
            """SELECT * FROM failure_info WHERE pipelinename=%s AND scheduleddate > 'now'::TIMESTAMP - '%s month'::INTERVAL;""",
            (pipeline_name, months_back))
        return self.connection().fetchall()

    def get_junit_failure_signature(self, stageid):
        self.connection().execute(
            """SELECT failuretype, failuretest FROM junitfailure WHERE stageid=%s ORDER BY failuretest ;""", (stageid,))
        return self.connection().fetchall()

    def get_texttest_document_statistics(self, pipeline_name):
        self.connection().execute("""SELECT * FROM all_data WHERE pipelinename=%s;""", (pipeline_name,))
        return self.connection().fetchall()

    def get_texttest_document_names(self, pipeline_name):
        self.connection().execute("""SELECT documentname FROM all_data WHERE pipelinename=%s;""", (pipeline_name,))
        return map(lambda x: x[0], self.connection().fetchall())

    def get_texttest_failures(self, pipeline_name):
        self.connection().execute("""SELECT * FROM texttestfailure;""", (pipeline_name,))
        return self.connection().fetchall()

    def get_stage_texttest_failures(self, stage_id):
        self.connection().execute("""SELECT * FROM texttestfailure WHERE stageid=%s;""", (stage_id,))
        return self.connection().fetchall()

    def get_synced_pipelines(self):
        self.connection().execute("""SELECT pipelinename, max(counter) FROM pipeline GROUP BY pipelinename;""")
        return self.connection().fetchall()

    def fetch_current_stage(self, pipeline_name):
        self.connection().execute(
            """SELECT * FROM failure_info WHERE pipelinename = %s ORDER BY counter DESC, stageindex DESC;""",
            (pipeline_name,))

        return self.connection().fetchone()

    def truncate_tables(self):
        self.connection().execute("TRUNCATE failureinformation, junitfailure, pipeline, stage, texttestfailure")

    def fetch_previous_stage(self, pipeline_name, pipeline_counter, current_stage_index):
        sql = """(SELECT * FROM failure_info WHERE pipelinename = %s AND counter = %s AND stageindex < %s
            UNION
            SELECT * FROM failure_info WHERE pipelinename = %s AND counter = %s - 1)
            ORDER BY counter DESC, stageindex DESC;"""

        query_tuple = (pipeline_name, pipeline_counter, current_stage_index, pipeline_name, pipeline_counter)

        self.connection().execute(sql, query_tuple)
        return self.connection().fetchone()

    def fetch_latest_passing_stage(self, pipeline_name):
        self.connection().execute(
            """SELECT * FROM failure_info WHERE pipelinename = %s AND result = 'Passed' ORDER BY counter DESC, stageindex DESC;""",
            (pipeline_name,))
        return self.connection().fetchone()

_connection = None


def create_connection(db_port=15554):
    global _connection
    if not _connection:
        _connection = SQLConnection(db_port)
    return _connection


def get_connection():
    if not _connection:
        raise ValueError("Database connection not instantiated")
    return _connection
