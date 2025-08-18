# Dockerfile for scheduler service
FROM python:3.10-slim

ENV USER steamcmd
ENV HOME /data

ENV PORT 8000
ENV WORKERS 4

COPY services/scheduler/requirements.txt /tmp/requirements.txt
RUN pip3 install --no-cache-dir -r /tmp/requirements.txt \
 && rm /tmp/requirements.txt

RUN useradd -m -d $HOME $USER
USER $USER
WORKDIR $HOME

COPY --chown=$USER:$USER services/scheduler/source/ $HOME/
COPY --chown=$USER:$USER libraries/python/utils/ $HOME/utils

CMD ["python", "main.py"]