#
#  file: migrations/0001.create-base.py
#
from yoyo import step

steps = [
    step("""CREATE TABLE pipeline_instance(
              id INTEGER NOT NULL PRIMARY KEY,
              pipeline_name TEXT,
              pipeline_counter INTEGER,
              trigger_message TEXT
            );
    """,
         "DROP TABLE pipeline_instance;"),

    step("""CREATE TABLE stage(
              id INTEGER NOT NULL PRIMARY KEY,
              instance_id INTEGER,
              stage_counter INTEGER,
              name TEXT,
              approved_by TEXT,
              scheduled_date TIMESTAMP,
              result TEXT
            );""",
         "DROP TABLE stage;"),

    step("""CREATE TABLE job(
              id INTEGER NOT NULL PRIMARY KEY,
              stage_id INTEGER,
              name TEXT,
              agent_uuid TEXT,
              scheduled_date TIMESTAMP,
              result TEXT,
              tests_run INTEGER,
              tests_failed INTEGER,
              tests_skipped INTEGER
            );""",
         "DROP TABLE job;"),

    step("""CREATE TABLE agent(
              id TEXT NOT NULL PRIMARY KEY,
              agent_name TEXT
            );""",
         "DROP TABLE agent;"),

    step("""CREATE TABLE texttest_failure(
              id SERIAL PRIMARY KEY,
              stage_id INTEGER,
              test_index INTEGER,
              failure_type TEXT,
              document_name TEXT
            );""",
         "DROP TABLE texttest_failure;"),

    step("""CREATE TABLE failure_information(
              id SERIAL PRIMARY KEY,
              stage_id INTEGER,
              failure_stage TEXT
            );""",
         "DROP TABLE failure_information;"),

    step("""CREATE TABLE junit_failure(
              id SERIAL PRIMARY KEY,
              stage_id INTEGER,
              failure_type TEXT,
              failure_test TEXT
            );""",
         "DROP TABLE junit_failure;"),

    step("""CREATE TABLE stage_claim(
              id SERIAL PRIMARY KEY ,
              stage_id INTEGER,
              responsible TEXT,
              description TEXT);""",
         "DROP TABLE stage_claim;")
]
