#
#  file: migrations/0002.create-views.py
#
from yoyo import step
#
steps = [
    step("""CREATE VIEW final_stages AS
            SELECT s.*
            FROM stage s
            JOIN
            (SELECT instance_id, max(stage_counter) as stage_counter, name
            FROM stage
            GROUP BY instance_id, name) sa
            ON s.instance_id = sa.instance_id AND s.stage_counter = sa.stage_counter AND s.name = sa.name;""",
         "DROP VIEW final_stages;"),

    step("""CREATE VIEW run_outcomes AS
            SELECT pi.*, outcome
            FROM pipeline_instance pi
            JOIN (
                SELECT instance_id, min(result) as outcome
                FROM final_stages f
                JOIN pipeline_instance p
                ON f.instance_id = p.id
                GROUP BY instance_id
            ) px
            ON px.instance_id = pi.id
            ORDER BY pipeline_counter DESC""",
         "DROP VIEW run_outcomes;"),

    step("""CREATE VIEW latest_intervals AS
            WITH max_failing as (
            SELECT pipeline_name, max(pipeline_counter) as fail_counter FROM run_outcomes WHERE outcome = 'Failed' GROUP BY pipeline_name
            ), max_passing as (
            SELECT pipeline_name, max(pipeline_counter) as pass_counter FROM run_outcomes WHERE outcome = 'Passed' GROUP BY pipeline_name
            )
            SELECT mf.pipeline_name, fail_counter, pass_counter, (fail_counter < pass_counter) as currently_passing
            FROM max_failing mf
            JOIN max_passing ms
            ON mf.pipeline_name = ms.pipeline_name""",
         "DROP VIEW latest_intervals;"),

    step("""CREATE VIEW active_claims AS
            SELECT i.* FROM instance_claim i
            JOIN (SELECT pipeline_name, max(pipeline_counter) as pipeline_counter FROM instance_claim GROUP BY pipeline_name) ia
            ON i.pipeline_name = ia.pipeline_name AND i.pipeline_counter = ia.pipeline_counter
            JOIN (
                SELECT l.*, p.pipeline_counter as current_pipeline
                FROM latest_intervals l
            JOIN (
                SELECT pipeline_name, max(pipeline_counter) AS pipeline_counter
                FROM pipeline_instance pi
                JOIN stage s ON pi.id = s.instance_id
                GROUP BY pipeline_name
            ) p
            ON l.pipeline_name = p.pipeline_name
            WHERE currently_passing = false
            ) lf
            ON i.pipeline_name = lf.pipeline_name AND lf.pass_counter < i.pipeline_counter AND i.pipeline_counter <= lf.current_pipeline;""",
         "DROP VIEW active_claims;"),

    step("""CREATE VIEW failure_info AS
            SELECT p.pipeline_name, p.pipeline_counter, s.stage_counter, s.id, s.name as stage_name, p.trigger_message, s.approved_by, s.result, f.failure_stage, ac.responsible, ac.description, s.scheduled_date
            FROM pipeline_instance p
            JOIN stage s ON s.instance_id = p.id
            LEFT JOIN failure_information f ON f.stage_id = s.id
            LEFT JOIN active_claims ac ON ac.pipeline_name = p.pipeline_name AND ac.pipeline_counter <= p.pipeline_counter
            WHERE s.result <> 'Cancelled'
            ORDER BY p.pipeline_counter DESC, s.stage_counter DESC;""",
         "DROP VIEW failure_info;"),

    step("""CREATE VIEW graph_statistics AS
            SELECT p.pipeline_name, p.pipeline_counter, s.stage_counter, s.name as stage_name, s.result as stage_result, j.name as job_name, j.scheduled_date, j.result as job_result, f.failure_stage, a.agent_name, j.tests_run, j.tests_failed, j.tests_skipped
            FROM pipeline_instance p
            JOIN stage s ON s.instance_id = p.id
            JOIN job j ON j.stage_id = s.id
            JOIN agent a ON a.id = j.agent_uuid
            LEFT JOIN failure_information f ON f.stage_id = s.id;""",
         "DROP VIEW graph_statistics;"),

    step("""CREATE VIEW graph_statistics_final_stages AS
            SELECT p.pipeline_name, p.pipeline_counter, s.stage_counter, s.name as stage_name, s.result as stage_result, j.name as job_name, j.scheduled_date, j.result as job_result, f.failure_stage, a.agent_name, j.tests_run, j.tests_failed, j.tests_skipped
            FROM pipeline_instance p
            JOIN final_stages s ON s.instance_id = p.id
            JOIN job j ON j.stage_id = s.id
            JOIN agent a ON a.id = j.agent_uuid
            LEFT JOIN failure_information f ON f.stage_id = s.id;""",
         "DROP VIEW graph_statistics_final_stages")
]
