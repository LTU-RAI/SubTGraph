FROM python:3.10-slim

RUN mkdir /workspace
COPY rai-subtgraph /workspace/rai-subtgraph

RUN apt-get install gcc
RUN cd /workspace/rai-subtgraph && \
    python3 -m pip install -e .  --config-settings editable_mode=compat

WORKDIR /workspace/rai-subtgraph