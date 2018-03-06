from rq import Queue
from apiowm import get_data
import time

counter = 0
while counter != 4:
    get_data()
    # print('sleeping 10 sec')
    time.sleep(86400)
    # print('awake')
    counter += 1
