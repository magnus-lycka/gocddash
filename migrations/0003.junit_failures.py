from yoyo import step

steps = [
    step("""CREATE TABLE junitfailure(
              id SERIAL PRIMARY KEY,
              stageid INTEGER,
              failuretype TEXT,
              failuretest TEXT
            );""",
         "DROP TABLE junitfailure;")
]