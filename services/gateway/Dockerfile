# Set the base image
FROM python:3.10-slim

# Set environment variables
ENV USER steamcmd
ENV HOME /app

ENV PORT 8000
ENV WORKERS 4

################## BEGIN INSTALLATION ######################

# Install Python requirements
COPY services/gateway/requirements.txt /tmp/requirements.txt
RUN pip3 install --no-cache-dir "uvicorn[standard]" gunicorn \
 && pip3 install --no-cache-dir -r /tmp/requirements.txt \
 && rm /tmp/requirements.txt

# Create the application user
RUN useradd -m -d $HOME $USER

# Switch user and set working dir
USER $USER
WORKDIR $HOME

# Copy application code
COPY --chown=$USER:$USER services/gateway/source/ $HOME/
COPY --chown=$USER:$USER libraries/python/utils/ $HOME/utils

##################### INSTALLATION END #####################

# Set default container command
CMD exec gunicorn main:app --max-requests 3000 --max-requests-jitter 150 --workers $WORKERS --worker-class uvicorn.workers.UvicornWorker --bind 0.0.0.0:$PORT