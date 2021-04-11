# Set the base image steamcmd
FROM steamcmd/steamcmd:ubuntu-18

# Set environment variables
ENV USER steamcmd
ENV HOME /data

ENV PORT 8080
ENV WORKERS 1
ENV THREADS 8
ENV TIMEOUT 120

################## BEGIN INSTALLATION ######################

# Update the repository and install prerequisites
ARG DEBIAN_FRONTEND=noninteractive
RUN apt-get update \
 && apt-get install -y --no-install-recommends lib32stdc++6 python3 python3-pip \
 && rm -rf /var/lib/apt/lists/*

# Install Python requirements
COPY requirements.txt /tmp/requirements.txt
RUN pip3 install -U pip setuptools \
 && pip3 install --no-cache-dir -r /tmp/requirements.txt \
 && rm /tmp/requirements.txt

# Create the application user
RUN useradd -m -d $HOME $USER

# Switch user and set working dir
USER $USER
WORKDIR $HOME

# Copy application code
COPY src/ $HOME/

##################### INSTALLATION END #####################

# Set default container command
ENTRYPOINT [""]
CMD gunicorn --workers $WORKERS --threads $THREADS --timeout $TIMEOUT --bind :$PORT run:app
