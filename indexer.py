#!/usr/bin/env python
import pika
import celery_indexer
import logging
from librabbitmq import Connection






logger = logging.getLogger('myapp')
hdlr = logging.FileHandler('/var/tmp/myapp.log')
formatter = logging.Formatter('%(asctime)s %(levelname)s %(message)s')
hdlr.setFormatter(formatter)
logger.addHandler(hdlr)
logger.setLevel(logging.WARNING)


connection = pika.BlockingConnection(pika.ConnectionParameters(
        host='localhost'))
channel = connection.channel()


#from librabbitmq import Connection

#conn = Connection(host="localhost", userid="guest",
#                   password="guest", virtual_host="/")

#channel = conn.channel()
#channel.exchange_declare(exchange, type, ...)
#channel.queue_declare(queue, ...)
#channel.queue_bind('events')



#channel.queue_declare(queue='hello')
message_sent_counter =1
def callback(ch, method, properties, body):
    #print(" [x] Received %s" % body)
    celery_indexer.add_event.delay(body)
    #ch.basic_ack(delivery_tag=method.delivery_tag)
    global message_sent_counter
    message_sent_counter += 1
    if message_sent_counter % 100 == True:
        connection.process_data_events()

#def dump_message(message):

#        print("Body:'%s', Proeprties:'%s', DeliveryInfo:'%s'" % (
#                  message.body, message.properties, message.delivery_info))
#        celery_indexer.add_event.delay(str(message.body))
#        message.ack()

#channel.basic_consume('events',callback=dump_message)

#while True:
#    conn.drain_events()
    #string_body = body

    # prepare a cursor object using cursor() method




#channel.basic_qos(prefetch_count=10)

channel.basic_consume(callback,
                      queue='events',no_ack=True)
channel.start_consuming()
#initSphinx()

print(' [*] Waiting for messages. To exit press CTRL+C')


#db.close()

#channel.start_consuming()