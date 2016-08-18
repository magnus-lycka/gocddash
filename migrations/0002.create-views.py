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

    step("""CREATE VIEW latest_fail_intervals AS
            WITH run_groups AS (
              SELECT pi.*, fs.result, (
                SELECT COUNT(*)
                FROM pipeline_instance pix
                JOIN final_stages fsx
                ON fsx.instance_id = pix.id
                WHERE pi.pipeline_name = pix.pipeline_name AND pi.pipeline_counter <= pix.pipeline_counter AND fs.result <> fsx.result
              ) AS rungroup
              FROM pipeline_instance pi
              JOIN final_stages fs
              ON fs.instance_id = pi.id
            ), fail_intervals AS (
              SELECT pipeline_name, result, MIN(pipeline_counter) AS start_counter, MAX(pipeline_counter) AS end_counter
              FROM run_groups
              WHERE result = 'Failed'
              GROUP BY result, rungroup, pipeline_name
            )
            SELECT pipeline_name, (SELECT max(pipeline_counter)
                FROM final_stages fxx
                JOIN pipeline_instance pxx
                ON fxx.instance_id = pxx.id
                JOIN (SELECT name
                    FROM final_stages f
                    JOIN pipeline_instance p
                    ON f.instance_id = p.id
                    WHERE pipeline_name = fiv.pipeline_name
                    GROUP BY name ORDER BY min(scheduled_date) DESC LIMIT 1) last_stage
                ON fxx.name = last_stage.name
            WHERE pipeline_name = fiv.pipeline_name and result = 'Passed') + 1 AS start_counter, max(end_counter) AS end_counter
            FROM fail_intervals fiv
            GROUP BY pipeline_name;""",
         "DROP VIEW latest_fail_intervals;"),

    step("""CREATE VIEW active_claims AS
            SELECT i.* FROM instance_claim i
            JOIN (SELECT pipeline_name, max(pipeline_counter) as pipeline_counter FROM instance_claim GROUP BY pipeline_name) ia
            ON i.pipeline_name = ia.pipeline_name AND i.pipeline_counter = ia.pipeline_counter
            JOIN latest_fail_intervals lf
            ON i.pipeline_name = lf.pipeline_name AND lf.start_counter <= i.pipeline_counter AND i.pipeline_counter <= lf.end_counter
            JOIN (
              SELECT pipeline_name, max(pipeline_counter) AS pipeline_counter
              FROM pipeline_instance pi
              JOIN stage s ON pi.id = s.instance_id
              GROUP BY pipeline_name
            ) p
            ON lf.pipeline_name = p.pipeline_name AND lf.end_counter = p.pipeline_counter;""",
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
