import bottle
from bottle import route, run, Bottle, request, response, static_file
import os
import sys
from datetime import datetime
import time
from functools import wraps
import logging
import random

logger = logging.getLogger('webapp')

# set up the logger
logger.setLevel(logging.INFO)
file_handler = logging.FileHandler('webapp.log')
formatter = logging.Formatter('%(levelname)s:%(module)s %(msg)s')
file_handler.setLevel(logging.DEBUG)
file_handler.setFormatter(formatter)
stdout_handler = logging.StreamHandler(sys.stdout)
stdout_handler.setLevel(logging.DEBUG)
stdout_handler.setFormatter(formatter)
logger.addHandler(file_handler)
logger.addHandler(stdout_handler)

def log_to_logger(fn):
    '''
    Wrap a Bottle request so that a log line is emitted after it's handled.
    (This decorator can be extended to take the desired logger as a param.)
    '''
    @wraps(fn)
    def _log_to_logger(*args, **kwargs):
        request_time = datetime.now()
        actual_response = fn(*args, **kwargs)
        # modify this to log exactly what you need:
        logger.info('%s %s %s %s %s' % (request_time,
                                        request.remote_addr,
                                        request.method,
                                        request.url,
                                        response.status))
        return actual_response
    return _log_to_logger


app = bottle.default_app()
# app.install(log_to_logger)

def lottery():
    granularity = 10 # 10 => you have a change out of 10 ...
    t = time.time()
    t = t * granularity - int(t) * granularity
    request_time_in_a_second = int(round(t))
    random_fraction_of_a_second = random.randint(0,granularity)
    return request_time_in_a_second, random_fraction_of_a_second
    

@app.route('/')
def hello_world():
    req_time, rand_time = lottery()
    message = os.getenv("MESSAGE", "<h1>Try again!</h1>")
    color = "white"
    if req_time == rand_time :
        color = "green"
        message = "<h1>You are the winner !</h1> \
                  <h2> Show this page to the presenter and you will get a nice Sticker !</h2>"
        logger.info('%s %s %s' % (datetime.now(), request.remote_addr, "WON"))

    else :
        logger.info('%s %s %s' % (datetime.now(), request.remote_addr, "LOST"))


    return f"<body bgcolor={color}> \
            <center>{message} \
            <h2>You picked up {req_time} and the answer is {rand_time}</h2> \
            <font color=\"red\" size=\"+300\"><p>I Love <p></font> \
            <image src=\"static/App-Runner.svg\" width=\"350\"></center> \
            </body>"

@route('/static/<file>')
def serve_pictures(file):
    return static_file(file, root='public-html/')

if __name__ == "__main__":
    run(host="0.0.0.0", port=8080, debug=True, reloader=True)