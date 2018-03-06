import os
import psycopg2
import redis
from rq import Worker, Queue, Connection

listen = ['high', 'default', 'low']

DATABASE_URL = os.environ['DATABASE_URL']
conn = psycopg2.connect(DATABASE_URL, sslmode='require')


if __name__ == '__main__':
    worker = Worker(map(Queue, listen))
    worker.work()
