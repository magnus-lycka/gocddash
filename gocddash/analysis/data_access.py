import psycopg2


class SQLConnection:
    def __init__(self, db_port):
        self.conn = None
        self.db_port = db_port
        
        # from yoyo import read_migrations, get_backend
        # backend = get_backend('postgresql://analysisappluser:analysisappluser@dev.localhost:15554/go-analysis')
        # migrations = read_migrations('migrations')
        # backend.apply_migrations(backend.to_apply(migrations))

        conn_string = "host='dev.localhost' dbname='go-analysis' user='analysisappluser' password='analysisappluser' port='{}'".format(self.db_port)
        conn = psycopg2.connect(conn_string)
        conn.autocommit = True
        self.conn = conn.cursor()

    def insert_pipeline(self, pipeline):
        self.conn.execute(
            """UPDATE pipeline SET pipelinename=%s WHERE id=%s""",
            (pipeline.pipeline_name, pipeline.pipeline_id))

        self.conn.execute(
            """INSERT INTO pipeline(pipelinename, id) SELECT %s, %s WHERE NOT EXISTS (SELECT 1 FROM pipeline WHERE id=%s);""",
            (pipeline.pipeline_name, pipeline.pipeline_id, pipeline.pipeline_id))

    def insert_pipeline_instance(self, instance):
        self.conn.execute(
            """UPDATE pipeline_instance SET id=%s, pipelinecounter=%s, triggermessage=%s WHERE id=%s;""",
            (instance.instance_id, instance.pipeline_counter, instance.trigger_message, instance.instance_id))

        self.conn.execute(
            """INSERT INTO pipeline_instance(id, pipelinecounter, triggermessage) SELECT %s, %s, %s WHERE NOT EXISTS (SELECT 1 FROM pipeline_instance WHERE id=%s);""",
            (instance.instance_id, instance.pipeline_counter, instance.trigger_message, instance.instance_id))

    def insert_stage(self, stage):
        self.conn.execute(
            """UPDATE stage SET id=%s, stage_counter=%s, name=%s, approvedby=%s, result=%s WHERE id=%s;""",
            (stage.stage_id, stage.stage_counter, stage.stage_name, stage.approved_by, stage.stage_result, stage.stage_id))

        self.conn.execute(
            """INSERT INTO stage(id, stage_counter, name=%s, approvedby, result) SELECT %s, %s, %s, %s, %s WHERE NOT EXISTS (SELECT 1 FROM stage WHERE id=%s);""",
            (stage.stage_id, stage.stage_counter, stage.stage_name, stage.approved_by, stage.stage_result, stage.stage_id))

    def insert_job(self, job):
        self.conn.execute(
            """UPDATE job SET id=%s, name=%s, agent_uuid=%s, scheduled_date=%s, result=%s WHERE id=%s;""",
            (job.job_id, job.job_name, job.agent_uuid, job.scheduled_date, job.job_result, job.job_id))

        self.conn.execute(
            """INSERT INTO job(id, name, agent_uuid, scheduled_date, result) SELECT %s, %s, %s, %s, %s WHERE NOT EXISTS (SELECT 1 FROM job WHERE id=%s);""",
            (job.job_id, job.job_name, job.agent_uuid, job.scheduled_date, job.job_result, job.job_id))


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

    def get_highest_pipeline_count(self, pipeline_name):
        self.conn.execute("""SELECT COALESCE(max(counter), 0) FROM pipeline WHERE pipelinename = %s""",
                                (pipeline_name,))
        return self.conn.fetchone()[0]

    def get_new_agents(self):
        self.conn.execute(
            """SELECT DISTINCT agentuuid FROM stage WHERE agentuuid IS NOT NULL EXCEPT SELECT id FROM agent""")
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

    def get_synced_pipelines(self):
        self.conn.execute("""SELECT pipelinename, max(counter) FROM pipeline GROUP BY pipelinename;""")
        return self.conn.fetchall()

    def fetch_current_stage(self, pipeline_name):
        self.conn.execute(
            """SELECT * FROM failure_info WHERE pipelinename = %s ORDER BY counter DESC, stageindex DESC;""",
            (pipeline_name,))

        return self.conn.fetchone()

    def truncate_tables(self):
        self.conn.execute("TRUNCATE failureinformation, junitfailure, pipeline, stage, texttestfailure")

    def fetch_previous_stage(self, pipeline_name, pipeline_counter, current_stage_index):
        sql = """(SELECT * FROM failure_info WHERE pipelinename = %s AND counter = %s AND stageindex < %s
            UNION
            SELECT * FROM failure_info WHERE pipelinename = %s AND counter = %s - 1)
            ORDER BY counter DESC, stageindex DESC;"""

        query_tuple = (pipeline_name, pipeline_counter, current_stage_index, pipeline_name, pipeline_counter)

        self.conn.execute(sql, query_tuple)
        return self.conn.fetchone()

    def fetch_latest_passing_stage(self, pipeline_name):
        self.conn.execute(
            """SELECT * FROM failure_info WHERE pipelinename = %s AND result = 'Passed' ORDER BY counter DESC, stageindex DESC;""",
            (pipeline_name,))
        return self.conn.fetchone()

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
