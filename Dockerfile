# Set the base image steamcmd
FROM python:3.13-slim

# Set environment variables
ENV USER steamcmd
ENV HOME /data

ENV PORT 8000
ENV WORKERS 4

################## BEGIN INSTALLATION ######################

# Install Python requirements
COPY requirements.txt /tmp/requirements.txt
RUN pip3 install --no-cache-dir "uvicorn[standard]" gunicorn \
 && pip3 install --no-cache-dir -r /tmp/requirements.txt \
 && rm /tmp/requirements.txt

# Create the application user
RUN useradd -m -d $HOME $USER

# Switch user and set working dir
USER $USER
WORKDIR $HOME

# Copy application code
COPY --chown=$USER:$USER src/ $HOME/

##################### INSTALLATION END #####################

# Set default container command
CMD exec gunicorn web:app --max-requests 3000 --max-requests-jitter 150 --workers $WORKERS --worker-class uvicorn.workers.UvicornWorker --bind 0.0.0.0:$PORT