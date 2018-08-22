from __future__ import absolute_import, unicode_literals
import shlex, sys, time, docker, subprocess, ast, redis, os, signal

from threading import Thread
from docker import types
import monitoring
from parameters import backend_experiment_db

job_workers = {}

def worker(container, node_id):
	# Add the worker to the monitoring
	monitoring.add_worker(node_id, container["service_name"])

	# Start the app in a new process
	process = subprocess.Popen(['python3','container_worker.py', str(node_id) ,str(container)])
	container['process'] = process

# Start the jqueuer_agent process
def start(node_id):
	# A list of controlled containers on the same node
	container_list = {}

	# Docker client
	client = None
	try:
		client = docker.from_env()
	except Exception as e:
		raise e

	# a counter to trace the dead containers
	current_update = 0

	while True:
		current_update += 1
		try:
			# Loop over the containers list
			for container in client.containers.list():
				container_obj = {}
				try:
					# Get container ID
					container_long_id = container.attrs['Id']

					# Get container's service name
					container_service_name = container.attrs['Config']['Labels']['com.docker.swarm.service.name']
					container_state_running = container.attrs['State']['Running']
					if (container_state_running != True):
						continue

					# Check if the service belongs to an experiment
					if (not backend_experiment_db.exists(container_service_name)):
						continue

					# Get the experiment data
					experiment = ast.literal_eval(backend_experiment_db.get(container_service_name))

					# Check if the container has been already added, if yes, update the current_update
					if (container_long_id in container_list):
						container_list[container_long_id]['current_update'] = current_update
						continue

					container_obj = {
						'id_long': container_long_id,
						'name': container.attrs['Name'], 
						'service_id': container.attrs['Config']['Labels']['com.docker.swarm.service.id'],
						'service_name': container_service_name,
						'task_id': container.attrs['Config']['Labels']['com.docker.swarm.task.id'],
						'task_name': container.attrs['Config']['Labels']['com.docker.swarm.task.name'],
						'hostname' : container.attrs['Config']['Hostname'],
						'ip_address': '',
						'created': container.attrs['Created'],
						'started': container.attrs['State']['StartedAt'],
						'experiment_id':experiment['experiment_id'], 
						'current_update': current_update ,
					}

					try:
						container_obj['ip_address'] = container.attrs['NetworkSettings']['Networks']['bridge']['IPAddress']

						# Start a new thread to control this container 
						job_worker_thread = Thread(target = worker, args = (container_obj, node_id,))
						job_worker_thread.start()
						container_list[container_long_id] = container_obj

					except Exception as e:
						pass
				except Exception as e:
					pass

			# Containers that should be deleted from the list because they aren't alive
			trash = []

			# Trash the containers which weren't updated in the last three rounds
			for container_id_temp in container_list:
				container_temp = container_list[container_id_temp]
				if (current_update - container_temp['current_update'] > 2 ):
					os.killpg(os.getpgid(container_temp['process'].pid), signal.SIGTERM)
					trash.append(container_id_temp)
			for x in trash:
				del container_list[x]

		except Exception as e:
		        time.sleep(0.5)

if __name__ == '__main__':
	if (len(sys.argv) > 1):
		node_id = sys.argv[1]
	else:
		node_id = "default_id_1"
	start(node_id)
