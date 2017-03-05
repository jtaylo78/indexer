#!/usr/bin/python

import psycopg2

conn = psycopg2.connect(database="chasm", user="postgres", password="postgres", host="127.0.0.1", port="5432")
print "Opened database successfully"

cur = conn.cursor()

cur.execute("INSERT INTO events (event_full) \
      VALUES ('asdfasdfsdfasdf')");


conn.commit()
print "Records created successfully";
conn.close()