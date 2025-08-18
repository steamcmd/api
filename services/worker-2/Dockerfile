# Set the base image steamcmd
FROM python:3.10-slim

# Set environment variables
ENV USER steamcmd
ENV HOME /data

ENV CONCURRENCY 10

################## BEGIN INSTALLATION ######################

# Install Python requirements
COPY services/worker/requirements.txt /tmp/requirements.txt
RUN pip3 install --no-cache-dir -r /tmp/requirements.txt \
 && rm /tmp/requirements.txt

# Create the application user
RUN useradd -m -d $HOME $USER

# Switch user and set working dir
USER $USER
WORKDIR $HOME

# Copy application code
COPY --chown=$USER:$USER services/worker/source/ $HOME/
COPY --chown=$USER:$USER libraries/python/utils/ $HOME/utils

##################### INSTALLATION END #####################

# Set default container command
CMD exec celery -A main worker --loglevel=info --concurrency=$CONCURRENCY --beat