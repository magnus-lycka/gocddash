#
#  file: migrations/0002.create-views.py
#
from yoyo import step
#
steps = [
    step("""CREATE VIEW failure_info AS
            SELECT p.pipeline_name, p.pipeline_counter, s.stage_counter, s.id, s.name as stage_name, p.trigger_message, s.approved_by, s.result, f.failure_stage, sc.responsible, sc.description, s.scheduled_date
            FROM pipeline_instance p
            JOIN stage s ON s.instance_id = p.id
            LEFT JOIN failureinformation f ON f.stage_id = s.id
            LEFT JOIN stage_claim sc ON sc.stage_id = s.id
            WHERE s.result <> 'Cancelled'
            ORDER BY p.pipeline_counter DESC, s.stage_counter DESC;""",
         "DROP VIEW failure_info;"),

    step("""CREATE VIEW graph_statistics AS
            SELECT p.pipeline_name, p.pipeline_counter, s.stage_counter, s.name as stage_name, s.result as stage_result, j.name as job_name, j.scheduled_date, j.result as job_result, a.agent_name, j.tests_run, j.tests_failed, j.tests_skipped
            FROM pipeline_instance p
            JOIN stage s ON s.instance_id = p.id
            JOIN job j ON j.stage_id = s.id
            JOIN agent a ON a.id = j.agent_uuid;""",
         "DROP VIEW graph_statistics;"),

    step("""CREATE VIEW final_stages AS
            SELECT s.*
            FROM stage s
            JOIN
            (SELECT instance_id, max(stage_counter) as stage_counter, name
            FROM stage
            GROUP BY instance_id, name) sa
            ON s.instance_id = sa.instance_id AND s.stage_counter = sa.stage_counter AND s.name = sa.name;""",
         "DROP VIEW final_stages;"),

    step("""CREATE VIEW graph_statistics_final_stages AS
            SELECT p.pipeline_name, p.pipeline_counter, s.stage_counter, s.name as stage_name, s.result as stage_result, j.name as job_name, j.scheduled_date, j.result as job_result, a.agent_name, j.tests_run, j.tests_failed, j.tests_skipped
            FROM pipeline_instance p
            JOIN final_stages s ON s.instance_id = p.id
            JOIN job j ON j.stage_id = s.id
            JOIN agent a ON a.id = j.agent_uuid;""",
         "DROP VIEW graph_statistics_final_stages")
]
