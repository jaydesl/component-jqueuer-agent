from __future__ import absolute_import, unicode_literals
import shlex, sys, time, docker, subprocess, ast, redis, os, signal

from pprint import pprint
from threading import Thread
from pprint import pprint
from docker import types
import monitoring
from parameters import backend_experiment_db

job_workers = {}

def worker(container, node_id):
	# Arguments you give on command line
	monitoring.add_worker(node_id, container["service_name"])
	process = subprocess.Popen(['python3','container_worker.py', str(node_id) ,str(container)])
	print("process: " + str(process))
	container['process'] = process
	#job_workers[container['container_long_id']] = {'container': container, 'process': process}
	#monitoring.terminate_worker(node_id, service_name)
	#print("Worker_main Output: " + str(output))

def start(node_id):
	print("Starting container feeder, Node: " + node_id)
	container_list = {}
	print("Before client init " + node_id)
	client = None
	try:
		client = docker.from_env()
	except Exception as e:
		raise e
	print("Docker Client: " + str(client))
	print("After client init " + node_id)
	current_update = 0
	while True:
		current_update += 1
		#print("New round - container feeder")
		try:
			for container in client.containers.list():
				#pprint(container.attrs)
				container_obj = {}
				try:
					container_long_id = container.attrs['Id']
					container_service_name = container.attrs['Config']['Labels']['com.docker.swarm.service.name']
					container_state_running = container.attrs['State']['Running']
					if (container_state_running != True):
						print("Container isn't running")
						continue
					if (not backend_experiment_db.exists(container_service_name)):
						#print("Container " + container_long_id + " belongs to non-watched service")
						continue
					experiment = ast.literal_eval(backend_experiment_db.get(container_service_name))

					if (container_long_id in container_list):
						#print("Container " + container_long_id + " has been added previously")
						container_list[container_long_id]['current_update'] = current_update
						continue
					print("Container " + container_long_id + " will be added now")

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

						print("------------------------ New contanier -------------------------")
						pprint(container_obj)
						print("------------------------ New contanier -------------------------")
						container_list[container_long_id] = container_obj

					except Exception as e:
						print("An error happened while sending the container to the Agent")
						pass
				except Exception as e:
					#print("It isn't a swarm service's container")
					pass
			trash = []
			for container_id_temp in container_list:
				container_temp = container_list[container_id_temp]
				if (current_update - container_temp['current_update'] > 2 ):
					print("This container should be deleted from the list since it doesn't exist anymore : " + str(container_id_temp))
					os.killpg(os.getpgid(container_temp['process'].pid), signal.SIGTERM)
					trash.append(container_id_temp)
			for x in trash:
				del container_list[x]

		except Exception as e:
			print("An error happened while iterating the container's list")
		time.sleep(0.5)

if __name__ == '__main__':
	if (len(sys.argv) > 1):
		node_id = sys.argv[1]
	else:
		node_id = "default_id_1"
	print("* Node_ID: " + str(sys.argv[1]))
	start(node_id)
