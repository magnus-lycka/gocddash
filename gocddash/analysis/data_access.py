import os
import sqlite3
from datetime import datetime, timedelta


class SQLConnection:
    _shared_state = {'conn': None}

    def __init__(self):
        self.__dict__ = self._shared_state
        if not self.conn:
            self.conn = sqlite3.connect('gocddash.sqlite3')
            self._init()

    def _init(self):
        my_dir = os.path.split(__file__)[0]
        path = os.path.join(my_dir, '..', 'database', 'setup.sql')
        with open(path) as sql_file:
            statements = sql_file.read().split('\n\n')
            for statement in statements:
                with self.conn:
                    cursor = self.conn.cursor()
                    cursor.execute(statement)

    def show_database(self):
        with self.conn:
            cur = self.conn.cursor()
            cur.execute("PRAGMA database_list")
            result = ''
            for row in cur.fetchall():
                result += "{} {} {}\n".format(row[0], row[1], row[2])
        return result

    def insert_pipeline_instance(self, instance):
        with self.conn:
            cursor = self.conn.cursor()
            cursor.execute(
                "INSERT INTO pipeline_instance "
                "(id, pipeline_name, pipeline_counter, trigger_message) "
                "VALUES (?, ?, ?, ?);",
                (instance.instance_id,
                 instance.pipeline_name,
                 instance.pipeline_counter,
                 instance.trigger_message)
            )

    def insert_stage(self, pipeline_instance_id, stage):
        with self.conn:
            cursor = self.conn.cursor()
            cursor.execute(
                "INSERT INTO stage "
                "(id, instance_id, stage_counter, name, approved_by, scheduled_date, result) "
                "VALUES (?, ?, ?, ?, ?, ?, ?);",
                (stage.stage_id, pipeline_instance_id, stage.stage_counter, stage.stage_name,
                 stage.approved_by, stage.scheduled_date, stage.stage_result))

    def insert_job(self, stage_id, job):
        with self.conn:
            cursor = self.conn.cursor()
            cursor.execute(
                "INSERT INTO job "
                "(id, stage_id, name, agent_uuid, scheduled_date, result, tests_run, tests_failed, tests_skipped) "
                "VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?);",
                (job.job_id, stage_id, job.job_name, job.agent_uuid, job.scheduled_date,
                 job.job_result, job.tests_run, job.tests_failed, job.tests_skipped))

    def insert_agent(self, id_, agent_name):
        with self.conn:
            cursor = self.conn.cursor()
            cursor.execute(
                "INSERT INTO agent (id, agent_name) VALUES (?, ?);", (id_, agent_name))

    def insert_texttest_failure(self, stage_id, test_index, failure_type, document_name):
        with self.conn:
            cursor = self.conn.cursor()
            cursor.execute(
                "INSERT INTO texttest_failure "
                "(stage_id, test_index, failure_type, document_name) "
                "VALUES (?, ?, ?, ?);",
                (stage_id, test_index, failure_type, document_name))

    def insert_failure_information(self, stage_id, failure_stage):
        with self.conn:
            cursor = self.conn.cursor()
            cursor.execute(
                "INSERT INTO failure_information "
                "(stage_id, failure_stage) "
                "VALUES (?, ?);",
                (stage_id, failure_stage))

    def insert_junit_failure_information(self, stage_id, failure_type, failure_test):
        with self.conn:
            cursor = self.conn.cursor()
            cursor.execute(
                "INSERT INTO junit_failure "
                "(stage_id, failure_type, failure_test) "
                "VALUES (?, ?, ?);",
                (stage_id, failure_type, failure_test))

    def insert_instance_claim(self, pipeline_name, pipeline_counter, responsible, desc):
        with self.conn:
            cursor = self.conn.cursor()
            cursor.execute(
                "INSERT INTO instance_claim "
                "(pipeline_name, pipeline_counter, responsible, description) "
                "VALUES (?, ? ,? ,?);",
                (pipeline_name, pipeline_counter, responsible, desc))

    def update_instance_claim(self, pipeline_name, pipeline_counter, responsible, desc):
        with self.conn:
            cursor = self.conn.cursor()
            cursor.execute(
                "UPDATE instance_claim "
                "SET pipeline_name=?, "
                "    pipeline_counter=?, "
                "    responsible=?, "
                "    description=? "
                "WHERE pipeline_name = ? AND "
                "      pipeline_counter = ?;",
                (pipeline_name,
                 pipeline_counter,
                 responsible,
                 desc,
                 pipeline_name,
                 pipeline_counter))

    def insert_email_notification_sent(self, pipeline_name, pipeline_counter):
        with self.conn:
            cursor = self.conn.cursor()
            cursor.execute(
                "INSERT INTO email_notifications "
                "(pipeline_name, pipeline_counter, sent) "
                "VALUES (%s, %s, now()) ",
                (pipeline_name, pipeline_counter)
            )

    def get_highest_pipeline_count(self, pipeline_name):
        with self.conn:
            cursor = self.conn.cursor()
            cursor.execute(
                "SELECT COALESCE(max(pipeline_counter), 0) "
                "FROM pipeline_instance "
                "WHERE pipeline_name = ?",
                (pipeline_name,))
            result = cursor.fetchone()[0]
        return result

    def get_new_agents(self):
        with self.conn:
            cursor = self.conn.cursor()
            cursor.execute("SELECT DISTINCT agent_uuid "
                           "FROM job "
                           "WHERE agent_uuid IS NOT NULL EXCEPT SELECT id FROM agent")
            result = map(lambda x: x[0], cursor.fetchall())
        return result

    def is_failure_downloaded(self, stage_id):
        with self.conn:
            cursor = self.conn.cursor()
            cursor.execute("SELECT * FROM failure_information WHERE stage_id=? ;", (stage_id,))

            fetchone = cursor.fetchone()
        return fetchone

    def get_failure_statistics(self, pipeline_name, months_back=1):
        with self.conn:
            cursor = self.conn.cursor()
            cursor.execute(
                "SELECT * "
                "FROM failure_info "
                "WHERE pipelinename=%s AND "
                "      scheduleddate > 'now'::TIMESTAMP - '%s month'::INTERVAL;",
                (pipeline_name, months_back)
            )
            fetchall = cursor.fetchall()
        return fetchall

    def get_junit_failure_signature(self, stage_id):
        with self.conn:
            cursor = self.conn.cursor()
            cursor.execute(
                "SELECT failure_type, failure_test "
                "FROM junit_failure "
                "WHERE stage_id=? ORDER BY failure_test ;",
                (stage_id,)
            )
            fetchall = cursor.fetchall()
        return fetchall

    def get_texttest_document_statistics(self, pipeline_name):
        with self.conn:
            cursor = self.conn.cursor()
            cursor.execute("SELECT * FROM all_data WHERE pipelinename=%s;", (pipeline_name,))
            fetchall = cursor.fetchall()
        return fetchall

    def get_texttest_document_names(self, pipeline_name):
        with self.conn:
            cursor = self.conn.cursor()
            cursor.execute("SELECT document_name FROM all_data WHERE pipelinename=%s;", (pipeline_name,))
            document_names = map(lambda x: x[0], cursor.fetchall())
        return document_names

    def get_texttest_failures(self, pipeline_name):
        with self.conn:
            cursor = self.conn.cursor()
            cursor.execute("SELECT * FROM texttest_failure;", (pipeline_name,))
            failures = cursor.fetchall()
        return failures

    def get_stage_texttest_failures(self, stage_id):
        with self.conn:
            cursor = self.conn.cursor()
            cursor.execute("SELECT * FROM texttest_failure WHERE stage_id=?;", (stage_id,))
            failures = cursor.fetchall()
        return failures

    def get_pipeline_head(self, pipeline_name):
        with self.conn:
            cursor = self.conn.cursor()
            cursor.execute("""SELECT f.* FROM
                            (SELECT pipeline_name, max(id) as stage_id FROM failure_info GROUP BY pipeline_name) s
                            JOIN failure_info f
                            ON s.stage_id = f.id
                            WHERE f.pipeline_name=?;""", (pipeline_name,))
            head = cursor.fetchone()
        return head

    def get_synced_pipeline_heads(self):
        with self.conn:
            cursor = self.conn.cursor()
            cursor.execute("""SELECT f.* FROM
                            (SELECT pipeline_name, max(id) as stage_id FROM failure_info GROUP BY pipeline_name) s
                            JOIN failure_info f
                            ON s.stage_id = f.id;""")
            synced_heads = cursor.fetchall()
        return synced_heads

    def fetch_current_stage(self, pipeline_name):
        with self.conn:
            cursor = self.conn.cursor()
            cursor.execute(
                "SELECT * "
                "FROM failure_info "
                "WHERE pipeline_name = ? "
                "ORDER BY pipeline_counter DESC, scheduled_date DESC, stage_counter DESC;",
                (pipeline_name,))
            current_stage = cursor.fetchone()
        return current_stage

    def truncate_tables(self):
        with self.conn:
            cursor = self.conn.cursor()
            cursor.execute("TRUNCATE failure_information, job, junit_failure, "
                           "pipeline_instance, stage, texttest_failure, instance_claim")

    def fetch_previous_stage(self, pipeline_name, pipeline_counter, current_stage_name, current_stage_counter):
        sql = """SELECT *
                    FROM failure_info
                    WHERE pipeline_name = ?
                    AND stage_name = ?
                    AND not (pipeline_counter = ?
                    AND stage_counter = ?)
                    ORDER BY pipeline_counter DESC, stage_counter DESC;"""
        query_tuple = (pipeline_name, current_stage_name, pipeline_counter, current_stage_counter)
        with self.conn:
            cursor = self.conn.cursor()
            cursor.execute(sql, query_tuple)
            prev_stage = cursor.fetchone()
        return prev_stage

    def get_stage_order(self, pipeline_name):
        with self.conn:
            cursor = self.conn.cursor()
            cursor.execute(
                "SELECT stage_name "
                "FROM failure_info "
                "WHERE pipeline_name = ? "
                "GROUP BY stage_name "
                "ORDER BY min(scheduled_date) ASC;",
                (pipeline_name,))
            stage_order = list(map(lambda x: x[0], cursor.fetchall()))
        return stage_order

    def fetch_latest_passing_stage(self, pipeline_name):
        with self.conn:
            cursor = self.conn.cursor()
            cursor.execute(
                """SELECT f.*
                FROM run_outcomes r
                JOIN failure_info f
                ON r.pipeline_name = f.pipeline_name AND
                   r.pipeline_counter = f.pipeline_counter
                WHERE f.pipeline_name = ?
                AND outcome = 'Passed'
                ORDER BY pipeline_counter DESC, stage_counter DESC;""",
                (pipeline_name,)
            )
            latest_passing_stage = cursor.fetchone()
        return latest_passing_stage

    def fetch_first_synced(self, pipeline_name):
        with self.conn:
            cursor = self.conn.cursor()
            cursor.execute(
                "SELECT * FROM failure_info WHERE pipeline_name = ? ORDER BY pipeline_counter LIMIT 1;",
                (pipeline_name,))
            first_synced = cursor.fetchone()
        return first_synced

    def claim_exists(self, pipeline_name, pipeline_counter):
        with self.conn:
            cursor = self.conn.cursor()
            cursor.execute(
                "SELECT * FROM instance_claim WHERE pipeline_name = ? AND pipeline_counter = ?;",
                (pipeline_name, pipeline_counter)
            )
            claim_ = cursor.fetchone() is not None
        return claim_

    def get_graph_statistics_for_pipeline(self, pipeline_name):
        with self.conn:
            cursor = self.conn.cursor()
            cursor.execute(
                "SELECT * "
                "FROM graph_statistics "
                "WHERE pipeline_name = ?", (pipeline_name,)
            )
            graph_statistics = cursor.fetchall()
        return graph_statistics

    def get_graph_statistics(self, days_limit, pipeline_name):
        pipeline_name = pipeline_name or "%"
        if days_limit:
            start = datetime.now() - timedelta(days=days_limit)
        else:
            start = '2000-01-01 00:00:00.000000'
        with self.conn:
            cursor = self.conn.cursor()
            cursor.execute(
                "SELECT * "
                "FROM graph_statistics "
                "WHERE agent_name NOT LIKE 'UNKNOWN%' "
                "AND pipeline_name LIKE ? "
                "AND scheduled_date > ?;",
                (pipeline_name, start )
            )
            graph_statistics = cursor.fetchall()
        return graph_statistics

    def get_graph_statistics_for_final_stages(self, pipeline_name):
        with self.conn:
            cursor = self.conn.cursor()
            cursor.execute(
                "SELECT * "
                "FROM graph_statistics_final_stages "
                "WHERE pipeline_name = ? "
                "ORDER BY pipeline_counter ASC",
                (pipeline_name,)
            )
            graph_statistics = cursor.fetchall()
        return graph_statistics

    def get_jobs_by_stage_id(self, stage_id):
        with self.conn:
            cursor = self.conn.cursor()
            cursor.execute(
                "SELECT * "
                "FROM job "
                "WHERE stage_id = ? "
                "ORDER BY id",
                (stage_id,)
            )
            jobs = cursor.fetchall()
        return jobs

    def get_latest_synced_stage(self, pipeline_instance_id, stage_name):
        with self.conn:
            cursor = self.conn.cursor()
            cursor.execute(
                """SELECT COALESCE(max(stage_counter), 0)
                FROM pipeline_instance p
                JOIN stage s
                ON p.id = s.instance_id
                WHERE p.id = ? AND s.name = ?""", (pipeline_instance_id, stage_name)
            )
            fetchone_ = cursor.fetchone()[0]
        return fetchone_

    def get_claims_for_unsynced_pipelines(self):
        with self.conn:
            cursor = self.conn.cursor()
            cursor.execute(
                "SELECT i.pipeline_name, i.pipeline_counter, i.responsible, i.description "
                "FROM instance_claim i "
                "JOIN ("
                "    SELECT pipeline_name, max(pipeline_counter) as pipeline_counter "
                "    FROM instance_claim WHERE pipeline_name NOT IN ("
                "        SELECT pipeline_name FROM pipeline_instance"
                "    )"
                "    GROUP BY pipeline_name"
                ") gi ON i.pipeline_name = gi.pipeline_name AND i.pipeline_counter = gi.pipeline_counter;"
            )
            fetchall = cursor.fetchall()
        return fetchall

    def pipeline_instance_exists(self, pipeline_name, pipeline_counter):
        with self.conn:
            cursor = self.conn.cursor()
            cursor.execute("SELECT * "
                           "FROM pipeline_instance "
                           "WHERE pipeline_name = ? AND pipeline_counter = ?",
                           (pipeline_name, pipeline_counter))
            instance_exists = cursor.fetchone() is not None
        return instance_exists

    def get_latest_failure_streak(self, pipeline_name):
        with self.conn:
            cursor = self.conn.cursor()
            cursor.execute("SELECT * "
                           "FROM latest_intervals "
                           "WHERE pipeline_name = ?",
                           (pipeline_name,))
            fetchone = cursor.fetchone()
        return fetchone

    def email_notification_sent_for_current_streak(self, pipeline_name):
        with self.conn:
            cursor = self.conn.cursor()
            cursor.execute(
                "SELECT e.* "
                "FROM latest_intervals l "
                "JOIN email_notifications e ON "
                "  l.pipeline_name = e.pipeline_name AND "
                "  l.pass_counter < e.pipeline_counter AND "
                "  l.currently_passing = 0 "
                "WHERE l.pipeline_name = ?;",
                (pipeline_name,))
            mail_sent = cursor.fetchone() is not None
        return mail_sent


def get_connection():
    return SQLConnection()
