import redis
import os

JOB_QUEUE_PREFIX        =       'jqueue_service_'
broker_protocol         =       'pyamqp'
broker_username         =       'admin'
broker_password         =       'mypass'
broker_server           =       os.getenv('JQ_SERVER', "rabbit") # This value should be changed to the jqueuer_server Ip address
broker_port             =       5672

def broker():
        broker  =       broker_protocol + '://' + broker_username
        if (broker_password != ''):
                broker  = broker + ':' + broker_password
        broker  =       broker + '@' + broker_server + ':' + str(broker_port) + '//'
        return broker

# Redis backend configuration
backend_protocol                        =       'redis'
backend_server                          =       os.getenv('JQ_SERVER', "redis") # This value should be changed to the jqueuer_server Ip address
backend_port                            =       6379
backend_db                              =       0
backend_experiment_db_id                =       10

backend_experiment_db = redis.StrictRedis(
        host=backend_server,
        port=backend_port,
        db=backend_experiment_db_id,
        password='b4sic',
        charset="utf-8",
        decode_responses=True
        )

def backend(db):
        backend = backend_protocol + '://' + backend_server + ':' + str(backend_port) + '/' + str(db)
        return backend



# Prometheus exporer configuration
STATSD_SERVER   = os.getenv('JQ_SERVER', "statsd") # This value should be changed to the micado_master Ip address
STATSD_PORT     = 9125
STATSD_OPTIONS  = {
    'api_key':'jqueuer_api_key',
    'app_key':'jqueuer_app_key',
    'statsd_host': STATSD_SERVER,
    'statsd_port': STATSD_PORT
}
from datadog import initialize
initialize(**STATSD_OPTIONS)
from datadog import statsd
