from prometheus_client import Counter, Gauge, Histogram
import time, sys
from parameters import statsd

#JQUEUER_WORKER_ADDED_COUNT = 'jqueuer_worker_added_count'
JQUEUER_WORKER_COUNT = "jqueuer_worker_count" 
def add_worker(node_id, service_name):
	statsd.increment(JQUEUER_WORKER_COUNT,
		tags=[
			'node_id:%s' % node_id,
			'service_name:%s' % service_name,
		]
	)

#JQUEUER_WORKER_TERMINATED_COUNT = 'jqueuer_worker_terminated_count'
def terminate_worker(node_id, service_name):
	statsd.decrement(JQUEUER_WORKER_COUNT,
		tags=[
			'node_id:%s' % node_id,
			'service_name:%s' % service_name,
		]
	)


JQUEUER_JOB_RUNNING = 'jqueuer_job_running'
JQUEUER_JOB_STARTED = 'jqueuer_job_started'
def run_job(node_id, experiment_id ,service_name, qworker_id, job_id):
	statsd.gauge(JQUEUER_JOB_RUNNING,
		1,
		tags=[
			'node_id:%s' % node_id,
			'experiment_id:%s' % experiment_id,
			'service_name:%s' % service_name,
			'qworker_id: %s' % qworker_id,
			'job_id: %s' % job_id,
		]
	)
	statsd.gauge(JQUEUER_JOB_STARTED,
		1,
		tags=[
			'node_id:%s' % node_id,
			'experiment_id:%s' % experiment_id,
			'service_name:%s' % service_name,
			'qworker_id: %s' % qworker_id,
			'job_id: %s' % job_id,
		]
	)

JQUEUER_JOB_ACCOMPLISHED = 'jqueuer_job_accomplished'
JQUEUER_JOB_ACCOMPLISHED_LATENCY = 'jqueuer_job_accomplished_latency'
def terminate_job(node_id, experiment_id ,service_name, qworker_id, job_id, start_time):
	elapsed_time = time.time() - start_time
	statsd.gauge(JQUEUER_JOB_ACCOMPLISHED_LATENCY,
		elapsed_time,
		tags=[
			'node_id:%s' % node_id,
			'experiment_id:%s' % experiment_id,
			'service_name:%s' % service_name,
			'qworker_id: %s' % qworker_id,
			'job_id: %s' % job_id,
		]
	)
	statsd.gauge(JQUEUER_JOB_ACCOMPLISHED,
		1,
		tags=[
			'node_id:%s' % node_id,
			'experiment_id:%s' % experiment_id,
			'service_name:%s' % service_name,
			'qworker_id: %s' % qworker_id,
			'job_id: %s' % job_id,
		]
	)
	statsd.gauge(JQUEUER_JOB_RUNNING,
		0,
		tags=[
			'node_id:%s' % node_id,
			'experiment_id:%s' % experiment_id,
			'service_name:%s' % service_name,
			'qworker_id: %s' % qworker_id,
			'job_id: %s' % job_id,
		]
	)

JQUEUER_JOB_FAILED = 'jqueuer_job_failed'
JQUEUER_JOB_FAILED_LATENCY = 'jqueuer_job_failed_latency'
def job_failed(node_id, experiment_id ,service_name, qworker_id, job_id, start_time):
	elapsed_time = time.time() - start_time
	statsd.gauge(JQUEUER_JOB_FAILED_LATENCY,
		elapsed_time,
		tags=[
			'node_id:%s' % node_id,
			'experiment_id:%s' % experiment_id,
			'service_name:%s' % service_name,
			'qworker_id: %s' % qworker_id,
			'job_id: %s' % job_id,
		]
	)
	statsd.gauge(JQUEUER_JOB_FAILED,
		1,
		tags=[
			'node_id:%s' % node_id,
			'experiment_id:%s' % experiment_id,
			'service_name:%s' % service_name,
			'qworker_id: %s' % qworker_id,
			'job_id: %s' % job_id,
		]
	)
	statsd.gauge(JQUEUER_JOB_RUNNING,
		0,
		tags=[
			'node_id:%s' % node_id,
			'experiment_id:%s' % experiment_id,
			'service_name:%s' % service_name,
			'qworker_id: %s' % qworker_id,
			'job_id: %s' % job_id,
		]
	)

JQUEUER_TASK_RUNNING = 'jqueuer_task_running'
JQUEUER_TASK_STARTED = 'jqueuer_task_started'
def run_task(node_id, experiment_id ,service_name, qworker_id, job_id, task_id):
	statsd.gauge(JQUEUER_TASK_RUNNING,
		1,
		tags=[
			'node_id:%s' % node_id,
			'experiment_id:%s' % experiment_id,
			'service_name:%s' % service_name,
			'qworker_id: %s' % qworker_id,
			'job_id: %s' % job_id,
			'task_id: %s' % task_id,
		]
	)
	statsd.gauge(JQUEUER_TASK_STARTED,
		1,
		tags=[
			'node_id:%s' % node_id,
			'experiment_id:%s' % experiment_id,
			'service_name:%s' % service_name,
			'qworker_id: %s' % qworker_id,
			'job_id: %s' % job_id,
			'task_id: %s' % task_id,
		]
	)

JQUEUER_TASK_ACCOMPLISHED = 'jqueuer_task_accomplished'
JQUEUER_TASK_ACCOMPLISHED_LATENCY = 'jqueuer_task_accomplished_latency'
def terminate_task(node_id, experiment_id ,service_name, qworker_id, job_id, task_id, start_time):
	elapsed_time = time.time() - start_time
	statsd.gauge(JQUEUER_TASK_ACCOMPLISHED_LATENCY,
		elapsed_time,
		tags=[
			'node_id:%s' % node_id,
			'experiment_id:%s' % experiment_id,
			'service_name:%s' % service_name,
			'qworker_id: %s' % qworker_id,
			'job_id: %s' % job_id,
			'task_id: %s' % task_id,
		]
	)
	statsd.gauge(JQUEUER_TASK_ACCOMPLISHED,
		1,
		tags=[
			'node_id:%s' % node_id,
			'experiment_id:%s' % experiment_id,
			'service_name:%s' % service_name,
			'qworker_id: %s' % qworker_id,
			'job_id: %s' % job_id,
			'task_id: %s' % task_id,
		]
	)
	statsd.gauge(JQUEUER_TASK_RUNNING,
		0,
		tags=[
			'node_id:%s' % node_id,
			'experiment_id:%s' % experiment_id,
			'service_name:%s' % service_name,
			'qworker_id: %s' % qworker_id,
			'job_id: %s' % job_id,
			'task_id: %s' % task_id,
		]
	)

JQUEUER_TASK_FAILED = 'jqueuer_task_failed'
JQUEUER_TASK_FAILED_LATENCY = 'jqueuer_task_failed_latency'
def task_failed(node_id, experiment_id ,service_name, qworker_id, job_id, task_id, start_time):
	elapsed_time = time.time() - start_time
	statsd.gauge(JQUEUER_TASK_FAILED_LATENCY,
		elapsed_time,
		tags=[
			'node_id:%s' % node_id,
			'experiment_id:%s' % experiment_id,
			'service_name:%s' % service_name,
			'qworker_id: %s' % qworker_id,
			'job_id: %s' % job_id,
			'task_id: %s' % task_id,
		]
	)
	statsd.gauge(JQUEUER_TASK_FAILED,
		1,
		tags=[
			'node_id:%s' % node_id,
			'experiment_id:%s' % experiment_id,
			'service_name:%s' % service_name,
			'qworker_id: %s' % qworker_id,
			'job_id: %s' % job_id,
			'task_id: %s' % task_id,
		]
	)
	statsd.gauge(JQUEUER_TASK_RUNNING,
		0,
		tags=[
			'node_id:%s' % node_id,
			'experiment_id:%s' % experiment_id,
			'service_name:%s' % service_name,
			'qworker_id: %s' % qworker_id,
			'job_id: %s' % job_id,
			'task_id: %s' % task_id,
		]
	)
