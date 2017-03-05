#!/usr/bin/env python
import MySQLdb
import logging
from celery import Celery
from celery import Task
import MySQLdb
from celery import Celery
import psycopg2
host = '127.0.0.1'
port = 9306
charset = 'utf8'
counter = 1
import time
try:
    import re2 as re
except ImportError:
    import re
else:
    re.set_fallback_notification(re.FALLBACK_WARNING)

field_dict = {}
field_regex = {}
app = Celery('indexer', backend='rpc://',broker='pyamqp://guest@localhost//')



def load_regex():
    field_regex['user'] = "\\s*Account\\s*Name:\\s*(\\S*)\\s+"
    field_regex['domain'] = "Account\\s?Domain:\\s*(\\S*)\\s+"
    field_regex['logonType'] = "Logon\\s?Type:\\s*(\\d*)\\s+"

    field_regex['User_1'] = "New\\s+Logon:\\s+.*\\s+Account\\s+Name:\\s+(\\S*)\\s+"
    field_regex['User_2'] = "New\\s+Logon:\\s+.*\\s+Account\\s+Name:\\s+.*\\s+\\s+Account\\s+Domain:\\s+(.*)\\s+"
    field_regex['processGuid']= "ProcessGuid:\\s{(\\S*)}"
    field_regex['image'] = "Image:\\s(.*)\\sComman"
    field_regex['commandLine'] = "CommandLine:\\s+(.*)\\s+CurrentDirectory"
    field_regex['currentDirectory'] = "CurrentDirectory:\\s+(.*)\\s+User"
    field_regex['user'] = "User:\\s+(.*)\\s+LogonGuid"
    field_regex['hashes'] = "Hashes:\\s+(\\S*)"
    field_regex['parentProcessGuid'] = "ParentProcessGuid:\\s?{(.*)}\\s?"
    field_regex['parentImage'] = "ParentImage:\\s?(.*)\\s?Parent"
    field_regex['parentCommandLine'] = "ParentCommandLine:\\s?(.*)"
    field_regex['eventType'] = "EventType:\\s+(\\S*)"
    field_regex['source'] = "\\sSource:\\s+(\\S*)"
    field_regex['integrityLevel'] = "\\sIntegrityLevel:\\s+(\\S*)"
    field_regex['utcTime'] = "\\sUtcTime:\\s+(.*)\\sProcessGuid"
    field_regex['eventId'] = "\\sEventID:\\s+(\\d+)"

def field_extract(event):
    for k,v in field_regex.items():
        match = re.search(v, event)
        if match:
            print "Match found field %s match %s" % (k,match.group(1))
            #print
        #print(k, v)


logger = logging.getLogger('myapp')
hdlr = logging.FileHandler('/var/tmp/myapp.log')
formatter = logging.Formatter('%(asctime)s %(levelname)s %(message)s')
hdlr.setFormatter(formatter)
logger.addHandler(hdlr)
logger.setLevel(logging.WARNING)

class DatabaseTask(Task):
    _db = None
    _cursor = None
    _count = 1
    @property
    def db(self):
        if self._db is None:
            self._db = psycopg2.connect(database="chasm", user="postgres", password="postgres", host="127.0.0.1", port="5432")
        return self._db



@app.task(base=DatabaseTask)
def add_event(event_text):
    print 'long time task begins'
    load_regex()
    field_extract(event_text)
    # time.sleep(1)
    #add_event.set_count(1)
    # Prepare SQL query to INSERT a record into the database.
    sql = "INSERT INTO events (\
                event_full) \
             VALUES ('%s')" % \
          (MySQLdb.escape_string(event_text))
    try:
          # Execute the SQL command
          cursor = add_event.db.cursor()
          cursor.execute(sql)
          global counter
          counter += 1
          # Commit your changes in the database
          if (counter % 1000 == 0):
              add_event.db.commit()
          cursor = None


    except Exception, e:
          logger.error("Error %s", event_text)
          logger.error(e, exc_info=True)
      #      # Rollback in case there is any error
      #      # db.rollback()
