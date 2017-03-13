#!/usr/bin/env python
import logging
from celery import Task
from celery import Celery
import psycopg2
import time
import MySQLdb
try:
    import re2 as re
except ImportError:
    import re
else:
    re.set_fallback_notification(re.FALLBACK_WARNING)


counter = 1
field_dict = {}
field_regex = {}

app = Celery('indexer', backend='rpc://',broker='pyamqp://guest@localhost//')



def load_regex():
    field_regex['user'] = "\\s*Account\\s*Name:\\s*(\\S*)\\s+"
    #field_regex['domain'] = "Account\\s?Domain:\\s*(\\S*)\\s+"
    #field_regex['logonType'] = "Logon\\s?Type:\\s*(\\d*)\\s+"
    #field_regex['user_1'] = "New\\s+Logon:\\s+.*\\s+Account\\s+Name:\\s+(\\S*)\\s+"
    #field_regex['user_2'] = "New\\s+Logon:\\s+.*\\s+Account\\s+Name:\\s+.*\\s+\\s+Account\\s+Domain:\\s+(.*)\\s+"
    field_regex['process_guid']= "ProcessGuid:\\s{(\\S*)}"
    field_regex['image'] = "Image:\\s(.*)\\sComman"
    field_regex['command_line'] = "CommandLine:\\s+(.*)\\s+CurrentDirectory"
    field_regex['current_directory'] = "CurrentDirectory:\\s+(.*)\\s+User"
    #field_regex['user'] = "User:\\s+(.*)\\s+LogonGuid"
    field_regex['hashes'] = "Hashes:\\s+(\\S*)"
    field_regex['parent_process_guid'] = "ParentProcessGuid:\\s?{(.*)}\\s?"
    field_regex['parent_image'] = "ParentImage:\\s?(.*)\\s?Parent"
    field_regex['parent_command_line'] = "ParentCommandLine:\\s?(.*)"
    #field_regex['event_type'] = "EventType:\\s+(\\S*)"
    field_regex['source'] = "\\sSource:\\s+(\\S*)"
    field_regex['integrity_level'] = "\\sIntegrityLevel:\\s+(\\S*)"
    field_regex['utc_time'] = "\\sUtcTime:\\s+(.*)\\sProcessGuid"
    field_regex['event_id'] = "\\sEventID:\\s+(\\d+)"



def field_extract(event):
    match_dict = {}
    for k,v in field_regex.items():
        match = re.search(v, event)
        if match:
            match_dict[k] = match.group(1)

    for k_1, v_1 in match_dict.items():
        print "Match found field %s match %s" % (k_1, v_1)
    match_dict['event_full'] = event
    placeholders = ', '.join(['%s'] * len(match_dict))
    columns = ', '.join(match_dict.keys())
    sql = "INSERT INTO events (%s) \
                 VALUES (%s) RETURNING id" % \
            (columns, placeholders)

    print sql
    try:

            # Execute the SQL command
            cursor = add_event.db.cursor()
            cursor.execute(sql, match_dict.values())
            #SPHINX RT Insert
            last_row_id =  cursor.fetchone()[0]
            print "last row %s" % last_row_id
            sql_sphinx = "INSERT INTO events (id,%s) \
                                 VALUES (%s,%s)" % \
                         (columns, last_row_id,placeholders)
            print sql_sphinx
            cursor_sphinx = add_event.sphinx.cursor()
            cursor_sphinx.execute(sql_sphinx, match_dict.values())

            global counter
            counter += 1
            # Commit your changes in the database
            if (counter % 1000 == 0):
                add_event.db.commit()
                add_event.sphinx.commit()
            #cursor = None
    except Exception, e:
            add_event.db.commit()
            add_event.sphinx.commit()
            logger.error("Error %s", event)
            logger.error(e, exc_info=True)
            time.sleep(50)





logger = logging.getLogger('myapp')
hdlr = logging.FileHandler('/var/tmp/myapp.log')
formatter = logging.Formatter('%(asctime)s %(levelname)s %(message)s')
hdlr.setFormatter(formatter)
logger.addHandler(hdlr)
logger.setLevel(logging.WARNING)


class DatabaseTask(Task):
    _sphinx = None
    _db = None
    _cursor = None
    _count = 1

    @property
    def db(self):
        if self._db is None:
            self._db = psycopg2.connect(database="chasm", user="postgres", password="postgres", host="127.0.0.1", port="5432")
        return self._db

    @property
    def sphinx(self):
        if self._sphinx is None:
            self._sphinx = MySQLdb.connect(host='127.0.0.1',port=9306)

        return self._sphinx


@app.task(base=DatabaseTask)
def add_event(event_text):
    print 'long time task begins'
    load_regex()
    field_extract(event_text)

