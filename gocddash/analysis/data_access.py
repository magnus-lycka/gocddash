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
        self.conn.execute(
            """INSERT INTO pipeline_instance(id, pipeline_name, pipeline_counter, trigger_message) VALUES (%s, %s, %s, %s);""",
            (instance.instance_id, instance.pipeline_name, instance.pipeline_counter, instance.trigger_message))

    def insert_stage(self, pipeline_instance_id, stage):
        self.conn.execute(
            """INSERT INTO stage(id, instance_id, stage_counter, name, approved_by, scheduled_date, result) VALUES (%s, %s, %s, %s, %s, %s, %s);""",
            (stage.stage_id, pipeline_instance_id, stage.stage_counter, stage.stage_name, stage.approved_by, stage.scheduled_date, stage.stage_result))

    def insert_job(self, stage_id, job):
        self.conn.execute(
            """INSERT INTO job(id, stage_id, name, agent_uuid, scheduled_date, result, tests_run, tests_failed, tests_skipped) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s);""",
            (job.job_id, stage_id, job.job_name, job.agent_uuid, job.scheduled_date, job.job_result, job.tests_run, job.tests_failed, job.tests_skipped))

    def insert_agent(self, id, agent_name):
        self.conn.execute("""INSERT INTO agent(id, agent_name) VALUES (%s, %s);""", (id, agent_name))

    def insert_texttest_failure(self, stage_id, test_index, failure_type, document_name):
        self.conn.execute(
            """INSERT INTO texttest_failure(stage_id, test_index, failure_type, document_name) VALUES (%s, %s, %s, %s);""",
            (stage_id, test_index, failure_type, document_name))

    def insert_failure_information(self, stage_id, failure_stage):
        self.conn.execute("""INSERT INTO failure_information(stage_id, failure_stage) VALUES (%s, %s);""",
                                (stage_id, failure_stage))

    def insert_junit_failure_information(self, stage_id, failure_type, failure_test):
        self.conn.execute("""INSERT INTO junit_failure(stage_id, failure_type, failure_test) VALUES (%s, %s, %s);""",
                          (stage_id, failure_type, failure_test))

    def insert_instance_claim(self, pipeline_name, pipeline_counter, responsible, desc):
        self.conn.execute("""INSERT INTO instance_claim(pipeline_name, pipeline_counter, responsible, description) VALUES (%s, %s, %s, %s);""",
                          (pipeline_name, pipeline_counter, responsible, desc))

    def update_instance_claim(self, pipeline_name, pipeline_counter, responsible, desc):
        self.conn.execute("""UPDATE instance_claim
                             SET pipeline_name=%s, pipeline_counter=%s, responsible=%s, description=%s
                             WHERE pipeline_name = %s AND pipeline_counter = %s;""",
                          (pipeline_name, pipeline_counter, responsible, desc, pipeline_name, pipeline_counter))

    def get_highest_pipeline_count(self, pipeline_name):
        self.conn.execute("""SELECT COALESCE(max(pipeline_counter), 0) FROM pipeline_instance WHERE pipeline_name = %s""",
                                (pipeline_name,))
        return self.conn.fetchone()[0]

    def get_new_agents(self):
        self.conn.execute(
            """SELECT DISTINCT agent_uuid FROM job WHERE agent_uuid IS NOT NULL EXCEPT SELECT id FROM agent""")
        return map(lambda x: x[0], self.conn.fetchall())

    def is_failure_downloaded(self, stage_id):
        self.conn.execute("""SELECT * FROM failure_information WHERE stage_id=%s ;""", (stage_id,))
        return self.conn.fetchone()

    def get_failure_statistics(self, pipeline_name, months_back=1):
        self.conn.execute(
            """SELECT * FROM failure_info WHERE pipelinename=%s AND scheduleddate > 'now'::TIMESTAMP - '%s month'::INTERVAL;""",
            (pipeline_name, months_back))
        return self.conn.fetchall()

    def get_junit_failure_signature(self, stage_id):
        self.conn.execute(
            """SELECT failure_type, failure_test FROM junit_failure WHERE stage_id=%s ORDER BY failure_test ;""", (stage_id,))
        return self.conn.fetchall()

    def get_texttest_document_statistics(self, pipeline_name):
        self.conn.execute("""SELECT * FROM all_data WHERE pipelinename=%s;""", (pipeline_name,))
        return self.conn.fetchall()

    def get_texttest_document_names(self, pipeline_name):
        self.conn.execute("""SELECT document_name FROM all_data WHERE pipelinename=%s;""", (pipeline_name,))
        return map(lambda x: x[0], self.conn.fetchall())

    def get_texttest_failures(self, pipeline_name):
        self.conn.execute("""SELECT * FROM texttest_failure;""", (pipeline_name,))
        return self.conn.fetchall()

    def get_stage_texttest_failures(self, stage_id):
        self.conn.execute("""SELECT * FROM texttest_failure WHERE stage_id=%s;""", (stage_id,))
        return self.conn.fetchall()

    def get_synced_pipeline_heads(self):
        self.conn.execute("""SELECT f.* FROM
                            (SELECT pipeline_name, max(id) as stage_id FROM failure_info GROUP BY pipeline_name) s
                            JOIN failure_info f
                            ON s.stage_id = f.id;""")
        return self.conn.fetchall()

    def fetch_current_stage(self, pipeline_name):
        self.conn.execute(
            """SELECT * FROM failure_info WHERE pipeline_name = %s ORDER BY pipeline_counter DESC, scheduled_date DESC, stage_counter DESC;""",
            (pipeline_name,))

        return self.conn.fetchone()

    def truncate_tables(self):
        self.conn.execute("TRUNCATE failure_information, job, junit_failure, pipeline_instance, stage, texttest_failure, instance_claim")

    def fetch_previous_stage(self, pipeline_name, pipeline_counter, current_stage_index, current_stage_name):
        sql = """SELECT *
                    FROM failure_info
                    WHERE pipeline_name = %s
                    AND stage_name = %s
                    AND not (pipeline_counter = %s
                    AND stage_counter = %s)
                    ORDER BY pipeline_counter DESC, stage_counter DESC;"""

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
            """SELECT * FROM failure_info WHERE pipeline_name = %s AND result = 'Passed' ORDER BY pipeline_counter DESC, stage_counter DESC;""",
            (pipeline_name,))
        return self.conn.fetchone()

    def fetch_first_synced(self, pipeline_name):
        self.conn.execute(
            """SELECT * FROM failure_info WHERE pipeline_name = %s ORDER BY pipeline_counter LIMIT 1;""",
            (pipeline_name,))
        return self.conn.fetchone()

    def claim_exists(self, pipeline_name, pipeline_counter):
        self.conn.execute(
            """SELECT * FROM instance_claim WHERE pipeline_name = %s AND pipeline_counter = %s;""", (pipeline_name, pipeline_counter)
        )
        return self.conn.fetchone() is not None

    def get_graph_statistics(self, pipeline_name):
        self.conn.execute(
            """SELECT * FROM graph_statistics WHERE pipeline_name = %s""", (pipeline_name,)
        )
        return self.conn.fetchall()

    def get_graph_statistics_for_final_stages(self, pipeline_name):
        self.conn.execute(
            """SELECT *
                FROM graph_statistics_final_stages
                WHERE pipeline_name = %s
                ORDER BY pipeline_counter ASC""", (pipeline_name,)
        )
        # Old 20 limit: AND pipeline_counter > (SELECT max(pipeline_counter) FROM pipeline_instance WHERE pipeline_name = %s)-20
        return self.conn.fetchall()

    def get_jobs_by_stage_id(self, stage_id):
        self.conn.execute(
            """SELECT * FROM job WHERE stage_id = %s ORDER BY id""", (stage_id,)
        )
        return self.conn.fetchall()

    def get_latest_synced_stage(self, pipeline_instance_id, stage_name):
        self.conn.execute(
            """SELECT COALESCE(max(stage_counter), 0)
                FROM pipeline_instance p
                JOIN stage s
                ON p.id = s.instance_id
                WHERE p.id = %s AND s.name = %s""", (pipeline_instance_id, stage_name)
        )
        return self.conn.fetchone()[0]

    def get_claims_for_unsynced_pipelines(self):
        self.conn.execute(
            """SELECT i.pipeline_name, i.pipeline_counter, i.responsible, i.description
                FROM instance_claim i
                JOIN (SELECT pipeline_name, max(pipeline_counter) as pipeline_counter FROM instance_claim WHERE pipeline_name NOT IN (
                 SELECT pipeline_name FROM pipeline_instance
                ) GROUP BY pipeline_name) gi
                ON i.pipeline_name = gi.pipeline_name AND i.pipeline_counter = gi.pipeline_counter;"""
        )
        return self.conn.fetchall()

_connection = None


def create_connection(db_port=15554):
    global _connection
    if not _connection:
        _connection = SQLConnection(db_port)
        return _connection
    raise ValueError("Database connection already instantiated - will not instantiate again.")


def get_connection():
    if not _connection:
        raise ValueError("Database connection not instantiated")
    return _connection
