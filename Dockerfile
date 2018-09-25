FROM python:3.6-slim
COPY requirements.txt /jqueuer_agent/requirements.txt
COPY job_operations.py /jqueuer_agent/job_operations.py
COPY container_worker.py /jqueuer_agent/container_worker.py
COPY monitoring.py /jqueuer_agent/monitoring.py
COPY jqueuer_agent.py /jqueuer_agent/jqueuer_agent.py
COPY parameters.py /jqueuer_agent/parameters.py
WORKDIR /jqueuer_agent/
RUN mkdir log
RUN mkdir data
RUN pip install -r requirements.txt
ENV NODE_ID=noname
ENTRYPOINT python3 jqueuer_agent.py $NODE_ID
