from __future__ import absolute_import, unicode_literals
import time, shlex, subprocess, random, sys, os

from container_worker import job_app
import container_worker as jqw
import monitoring
import celery
from celery.exceptions import Reject
from celery.result import AsyncResult

class JQueuer_Task(celery.Task):
	def on_failure(self, exc, task_id, args, kwargs, einfo):
		print('{0!r} failed: {1!r}'.format(task_id, exc))

index = 0
container_dead = False
@job_app.task(bind=True,acks_late=True, track_started=True, base=JQueuer_Task) # 
def add(self, exp_id, job_queue_id, job):
	global index, container_dead
	if (container_dead):
		time.sleep(30) 
		raise Reject('my container is dead', requeue=True)
	index = index +1
	job_params  = job['params']
	job_command 	= job['command']
	job_start_time = time.time()
	output = ""

	worker_id = self.request.hostname.split("@")[1]

	monitoring.run_job(getNodeID(worker_id), exp_id, getServiceName(worker_id), worker_id, job['id'])

	tasks = job['tasks']
	try:
		if (isinstance(tasks, list)):
			output = process_list(worker_id, exp_id, job_queue_id, job, job_start_time)
		else:
			output = process_array(worker_id, exp_id, job_queue_id, job, job_start_time)
		monitoring.terminate_job(getNodeID(worker_id), exp_id, getServiceName(worker_id), worker_id, job['id'], job_start_time)
	except subprocess.CalledProcessError as e:
		monitoring.job_failed(getNodeID(worker_id), exp_id, getServiceName(worker_id), worker_id, job['id'], job_start_time)
		container_dead = True
		self.update_state(state='RETRY')
		time.sleep(200)

	return output

def getNodeID(worker_id):
	return worker_id.split("##")[0]

def getServiceName(worker_id):
	return worker_id.split("##")[1]

def getContainerID(worker_id):
	return worker_id.split("##")[2]

def process_list(worker_id, exp_id, job_queue_id, job, job_start_time):
	output = ""
	for task in job['tasks']:
		try:
			task_command = task['command'] 
		except Exception as e:
			task['command'] = job['command']
		try:
			task_data = task['data'] 
		except Exception as e:
			tasks['data'] = job['data']
	
		task_start_time = time.time()
		monitoring.run_task(getNodeID(worker_id), exp_id,getServiceName(worker_id), worker_id, job['id'], task["id"])

		command = ['docker','exec', getContainerID(worker_id)] + task_command + task["data"] + [str(worker_id)]
		output = subprocess.check_output(command)
		monitoring.terminate_task(getNodeID(worker_id), exp_id, getServiceName(worker_id), worker_id, job['id'], task["id"], task_start_time)

	return output

def process_array(worker_id, exp_id, job_queue_id, job, job_start_time):
	output = ""
	tasks = job['tasks']
	try:
		task_command = tasks['command'] 
	except Exception as e:
		tasks['command'] = job['command']
	try:
		task_data = tasks['data'] 
	except Exception as e:
		tasks['data'] = job['data']

	for x in range(0,tasks['count']):
		task_start_time = time.time()
		task_id = tasks["id"] + "_" + str(x)
		monitoring.run_task(getNodeID(worker_id), exp_id, getServiceName(worker_id), worker_id, job['id'], task_id)
		command = ['docker','exec', getContainerID(worker_id)] + tasks['command'] + [str(tasks["data"]) + [str(worker_id)]]
		output = subprocess.check_output(command)
		monitoring.terminate_task(getNodeID(worker_id), exp_id, getServiceName(worker_id), worker_id, job['id'], task_id , task_start_time)

	return output


