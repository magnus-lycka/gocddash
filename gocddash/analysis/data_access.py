import psycopg2


class SQLConnection:
    def __init__(self, db_port):
        self.conn = None
        self.db_port = db_port

        conn_string = "host='dev.localhost' dbname='go-analysis' user='analysisappluser' password='analysisappluser' port='{}'".format(self.db_port)
        conn = psycopg2.connect(conn_string)
        conn.autocommit = True
        self.conn = conn.cursor()

    def insert_pipeline_instance(self, instance):
        # self.conn.execute(
        #     """UPDATE pipeline_instance SET id=%s, pipeline_name=%s, pipelinecounter=%s, triggermessage=%s WHERE id=%s;""",
        #     (instance.instance_id, instance.pipeline_name, instance.pipeline_counter, instance.trigger_message, instance.instance_id))

        self.conn.execute(
            """INSERT INTO pipeline_instance(id, pipeline_name, pipelinecounter, triggermessage) SELECT %s, %s, %s, %s WHERE NOT EXISTS (SELECT 1 FROM pipeline_instance WHERE id=%s);""",
            (instance.instance_id, instance.pipeline_name, instance.pipeline_counter, instance.trigger_message, instance.instance_id))

    def insert_stage(self, pipeline_instance_id, stage):
        # self.conn.execute(
        #     """UPDATE stage SET id=%s, instance_id=%s, stage_counter=%s, name=%s, approvedby=%s, result=%s WHERE id=%s;""",
        #     (stage.stage_id, pipeline_instance_id, stage.stage_counter, stage.stage_name, stage.approved_by, stage.stage_result, stage.stage_id))

        self.conn.execute(
            """INSERT INTO stage(id, instance_id, stage_counter, name, approvedby, scheduled_date, result) SELECT %s, %s, %s, %s, %s, %s, %s WHERE NOT EXISTS (SELECT 1 FROM stage WHERE id=%s);""",
            (stage.stage_id, pipeline_instance_id, stage.stage_counter, stage.stage_name, stage.approved_by, stage.scheduled_date, stage.stage_result, stage.stage_id))

    def insert_job(self, stage_id, job):
        self.conn.execute(
            """UPDATE job SET id=%s, stage_id=%s, name=%s, agent_uuid=%s, scheduled_date=%s, result=%s WHERE id=%s;""",
            (job.job_id, stage_id, job.job_name, job.agent_uuid, job.scheduled_date, job.job_result, job.job_id))

        self.conn.execute(
            """INSERT INTO job(id, stage_id, name, agent_uuid, scheduled_date, result) SELECT %s, %s, %s, %s, %s, %s WHERE NOT EXISTS (SELECT 1 FROM job WHERE id=%s);""",
            (job.job_id, stage_id, job.job_name, job.agent_uuid, job.scheduled_date, job.job_result, job.job_id))


    def insert_agent(self, id, agent_name):
        self.conn.execute("""INSERT INTO agent(id, agentname) VALUES (%s, %s);""", (id, agent_name))

    def insert_texttest_failure(self, stageid, testindex, failuretype, documentname):
        self.conn.execute(
            """INSERT INTO texttestfailure(stageid, testindex, failuretype, documentname) VALUES (%s, %s, %s, %s);""",
            (stageid, testindex, failuretype, documentname))

    def insert_failure_information(self, stageid, failurestage):
        self.conn.execute("""INSERT INTO failureinformation(stageid, failurestage) VALUES (%s, %s);""",
                                (stageid, failurestage))

    def insert_junit_failure_information(self, stageid, failure_type, failure_test):
        self.conn.execute("""INSERT INTO junitfailure(stageid, failuretype, failuretest) VALUES (%s, %s, %s);""",
                          (stageid, failure_type, failure_test))

    def insert_stage_claim(self, stageid, responsible, desc):
        self.conn.execute("""INSERT INTO stage_claim(stage_id, responsible, description) VALUES (%s, %s, %s);""",
                          (stageid, responsible, desc))

    def get_highest_pipeline_count(self, pipeline_name):
        self.conn.execute("""SELECT COALESCE(max(pipelinecounter), 0) FROM pipeline_instance WHERE pipeline_name = %s""",
                                (pipeline_name,))
        return self.conn.fetchone()[0]

    def get_new_agents(self):
        self.conn.execute(
            """SELECT DISTINCT agent_uuid FROM job WHERE agent_uuid IS NOT NULL EXCEPT SELECT id FROM agent""")
        return map(lambda x: x[0], self.conn.fetchall())

    def is_failure_downloaded(self, stage_id):
        self.conn.execute("""SELECT * FROM failureinformation WHERE stageid=%s ;""", (stage_id,))
        return self.conn.fetchone()

    def get_failure_statistics(self, pipeline_name, months_back=1):
        self.conn.execute(
            """SELECT * FROM failure_info WHERE pipelinename=%s AND scheduleddate > 'now'::TIMESTAMP - '%s month'::INTERVAL;""",
            (pipeline_name, months_back))
        return self.conn.fetchall()

    def get_junit_failure_signature(self, stageid):
        self.conn.execute(
            """SELECT failuretype, failuretest FROM junitfailure WHERE stageid=%s ORDER BY failuretest ;""", (stageid,))
        return self.conn.fetchall()

    def get_texttest_document_statistics(self, pipeline_name):
        self.conn.execute("""SELECT * FROM all_data WHERE pipelinename=%s;""", (pipeline_name,))
        return self.conn.fetchall()

    def get_texttest_document_names(self, pipeline_name):
        self.conn.execute("""SELECT documentname FROM all_data WHERE pipelinename=%s;""", (pipeline_name,))
        return map(lambda x: x[0], self.conn.fetchall())

    def get_texttest_failures(self, pipeline_name):
        self.conn.execute("""SELECT * FROM texttestfailure;""", (pipeline_name,))
        return self.conn.fetchall()

    def get_stage_texttest_failures(self, stage_id):
        self.conn.execute("""SELECT * FROM texttestfailure WHERE stageid=%s;""", (stage_id,))
        return self.conn.fetchall()

    def get_synced_pipelines_status(self):
        self.conn.execute("""SELECT s.pipeline_name, pipelinecounter, responsible, description FROM
                            (SELECT pipeline_name, max(id) as stage_id FROM failure_info GROUP BY pipeline_name) s
                            JOIN failure_info f
                            ON s.stage_id = f.id;""")
        return self.conn.fetchall()

    def fetch_current_stage(self, pipeline_name):
        self.conn.execute(
            """SELECT * FROM failure_info WHERE pipeline_name = %s ORDER BY pipelinecounter DESC, scheduled_date DESC, stage_counter DESC;""",
            (pipeline_name,))

        return self.conn.fetchone()

    def truncate_tables(self):
        self.conn.execute("TRUNCATE failureinformation, job, junitfailure, pipeline_instance, stage, texttestfailure, stage_claim")

    def fetch_previous_stage(self, pipeline_name, pipeline_counter, current_stage_index, current_stage_name):
        sql = """SELECT *
                    FROM failure_info
                    WHERE pipeline_name = %s
                    AND stage_name = %s
                    AND not (pipelinecounter = %s
                    AND stage_counter = %s)
                    ORDER BY pipelinecounter DESC, stage_counter DESC;"""

        query_tuple = (pipeline_name, current_stage_name, pipeline_counter, current_stage_index)

        self.conn.execute(sql, query_tuple)
        return self.conn.fetchone()

    def get_stage_order(self, pipeline_name):
        self.conn.execute(
            """SELECT stage_name FROM failure_info WHERE pipeline_name = %s GROUP BY stage_name ORDER BY min(scheduled_date) ASC;""",
            (pipeline_name,))
        return list(map(lambda x: x[0], self.conn.fetchall()))

    def fetch_latest_passing_stage(self, pipeline_name):
        self.conn.execute(
            """SELECT * FROM failure_info WHERE pipeline_name = %s AND result = 'Passed' ORDER BY pipelinecounter DESC, stage_counter DESC;""",
            (pipeline_name,))
        return self.conn.fetchone()

    def fetch_first_synced(self, pipeline_name):
        self.conn.execute(
            """SELECT * FROM failure_info WHERE pipeline_name = %s ORDER BY pipelinecounter LIMIT 1;""",
            (pipeline_name,))
        return self.conn.fetchone()

    def claim_exists(self, stage_id):
        self.conn.execute(
            """SELECT * FROM stage_claim WHERE stage_id = %s""", (stage_id,)
        )
        return self.conn.fetchone() is not None

_connection = None


def create_connection(db_port=15554):
    global _connection
    _connection = SQLConnection(db_port)
    return _connection


def get_connection():
    if not _connection:
        raise ValueError("Database connection not instantiated")
    return _connection
