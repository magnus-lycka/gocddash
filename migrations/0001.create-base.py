#
#  file: migrations/0001.create-base.py
#
from yoyo import step

steps = [
    step("""CREATE TABLE pipeline_instance(
              id INTEGER NOT NULL PRIMARY KEY,
              pipeline_name TEXT,
              pipelinecounter INTEGER,
              triggermessage TEXT
            );
    """,
         "DROP TABLE pipeline_instance;"),

    step("""CREATE TABLE stage(
              id INTEGER NOT NULL PRIMARY KEY,
              instance_id INTEGER,
              stage_counter INTEGER,
              name TEXT,
              approvedby TEXT,
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
              agentname TEXT
            );""",
         "DROP TABLE agent;"),

    step("""CREATE TABLE texttestfailure(
              id SERIAL PRIMARY KEY,
              stageid INTEGER,
              testindex INTEGER,
              failuretype TEXT,
              documentname TEXT
            );""",
         "DROP TABLE texttestfailure;"),

    step("""CREATE TABLE failureinformation(
              id SERIAL PRIMARY KEY,
              stageid INTEGER,
              failurestage TEXT
            );""",
         "DROP TABLE failureinformation;"),

    step("""CREATE TABLE junitfailure(
              id SERIAL PRIMARY KEY,
              stageid INTEGER,
              failuretype TEXT,
              failuretest TEXT
            );""",
         "DROP TABLE junitfailure;"),

    step("""CREATE TABLE stage_claim(
              id SERIAL PRIMARY KEY ,
              stage_id INTEGER,
              responsible TEXT,
              description TEXT);""",
         "DROP TABLE stage_claim;")
]
