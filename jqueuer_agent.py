from __future__ import absolute_import, unicode_literals
import shlex, sys, time, docker, subprocess, ast, redis, os, signal

from threading import Thread
from docker import types
import monitoring
from parameters import backend_experiment_db

job_workers = {}

def worker(container, node_id):
	monitoring.add_worker(node_id, container["service_name"])
	process = subprocess.Popen(['python3','container_worker.py', str(node_id) ,str(container)])
	container['process'] = process

def start(node_id):
	container_list = {}
	client = None
	try:
		client = docker.from_env()
	except Exception as e:
		raise e
	current_update = 0
	while True:
		current_update += 1
		try:
			for container in client.containers.list():
				container_obj = {}
				try:
					container_long_id = container.attrs['Id']
					container_service_name = container.attrs['Config']['Labels']['com.docker.swarm.service.name']
					container_state_running = container.attrs['State']['Running']
					if (container_state_running != True):
						continue
					if (not backend_experiment_db.exists(container_service_name)):
						continue
					experiment = ast.literal_eval(backend_experiment_db.get(container_service_name))

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

						job_worker_thread = Thread(target = worker, args = (container_obj, node_id,))
						job_worker_thread.start()
						container_list[container_long_id] = container_obj

					except Exception as e:
						pass
				except Exception as e:
					pass
			trash = []
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
