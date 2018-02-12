FROM python:3
ADD requirements.txt /jqueuer_agent/requirements.txt
ADD job_operations.py /jqueuer_agent/job_operations.py
ADD container_worker.py /jqueuer_agent/container_worker.py
ADD monitoring.py /jqueuer_agent/monitoring.py
ADD jqueuer_agent.py /jqueuer_agent/jqueuer_agent.py
ADD parameters.py /jqueuer_agent/parameters.py
WORKDIR /jqueuer_agent/
RUN mkdir log
RUN mkdir data
RUN pip install -r requirements.txt
RUN pip install -U "celery[redis]"
ENV NODE_ID=noname 
ENTRYPOINT python3 jqueuer_agent.py $NODE_ID