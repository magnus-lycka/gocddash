#
#  file: migrations/0001.create-base.py
#
from yoyo import step

steps = [
    step("""CREATE TABLE pipeline(
              id INTEGER NOT NULL PRIMARY KEY,
              stagecount INTEGER,
              pipelinename TEXT,
              counter INTEGER,
              triggermessage TEXT,
              UNIQUE (pipelinename, counter)
            );""",
         "DROP TABLE pipeline;"),

    step("""CREATE TABLE stage(
              id INTEGER NOT NULL PRIMARY KEY,
              approvedby TEXT,
              pipelinecounter INTEGER,
              pipelinename TEXT,
              stageindex INTEGER,
              result TEXT,
              scheduleddate TIMESTAMP,
              agentuuid TEXT,
              stagename TEXT
            );
    """,
         "DROP TABLE stage;"),

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
         "DROP TABLE failureinformation;")
]
