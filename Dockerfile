# Set the base image steamcmd
FROM jonakoudijs/steamcmd:latest

# File Author / Maintainer
LABEL maintainer="Jona Koudijs"

# Set environment variables
ENV USER steamcmd
ENV HOME /data

################## BEGIN INSTALLATION ######################

# Update the repository and install prerequisites
ARG DEBIAN_FRONTEND=noninteractive
RUN apt-get update \
 && apt-get install -y --no-install-recommends lib32stdc++6 python3 python3-pip \
 && pip3 install --no-cache-dir setuptools gunicorn \
 && rm -rf /var/lib/apt/lists/* \
 && pip3 uninstall pip -y

# Create the application user
RUN useradd -m -d $HOME $USER

# Switch user and set working dir
USER $USER
WORKDIR $HOME

# Copy configuration files
COPY src/ $HOME/

##################### INSTALLATION END #####################

# Set default container command
CMD gunicorn --workers 1 --threads 8 --timeout 120 --bind :$PORT run:app
