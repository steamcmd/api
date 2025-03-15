[![Build Status](https://github.com/steamcmd/api/actions/workflows/deploy.yml/badge.svg)](https://github.com/steamcmd/api/actions)
[![CodeFactor](https://www.codefactor.io/repository/github/steamcmd/api/badge)](https://www.codefactor.io/repository/github/steamcmd/api)
[![Code Style](https://img.shields.io/badge/code%20style-black-000000.svg)](https://github.com/python/black)
[![Discord Online](https://img.shields.io/discord/928592378711912488.svg)](https://discord.steamcmd.net)
[![Mastodon Follow](https://img.shields.io/mastodon/follow/109302774947550572?domain=https%3A%2F%2Ffosstodon.org&style=flat)](https://fosstodon.org/@steamcmd)
[![Image Size](https://img.shields.io/docker/image-size/steamcmd/api/latest.svg)](https://hub.docker.com/r/steamcmd/api)
[![Uptime Robot Uptime](https://img.shields.io/uptimerobot/ratio/m782827237-5067fd1d69e3b1b2e4e40fff)](https://status.steamcmd.net)
[![GitHub Release](https://img.shields.io/github/v/release/steamcmd/api?label=version)](https://github.com/steamcmd/api/releases)
[![GitHub Sponsors](https://img.shields.io/github/sponsors/steamcmd)](https://github.com/sponsors/steamcmd)
[![MIT License](https://img.shields.io/badge/license-MIT-blue.svg)](LICENSE)

# SteamCMD API

Read-only API interface for steamcmd app_info. The official API is reachable on
[api.steamcmd.net](https://api.steamcmd.net) and it's documentation can be found
on [www.steamcmd.net](https://www.steamcmd.net).

## Self-hosting

The API can easily be run via a container image which contains the API code and the
`uvicorn` tool to be able to respond to web requests. With every new version of
the API the Docker images is automatically rebuild and pushed to the Docker Hub:
```bash
docker pull steamcmd/api:latest
```
```bash
docker pull steamcmd/api:1.10.0
```
```bash
docker run -p 8000:8000 -d steamcmd/api:latest
```
The API consists of 2 services; the **Web** and the **Job** service and the Redis
cache. The **Job** service and the Redis cache are both optional but are both required
if you want to run the **Job** service.

Details on how the official API is hosted can be found in the
[platform](https://github.com/steamcmd/platform) repository. This repository contains
all the infrastructure as code that is used to deploy the API on a Kubernetes cluster.

See the [Development](#development) section for more information on running
the API and Job services directly via Python.

## Configuration

When hosting the API yourself there are few settings you can change to configure
the API to your platform specifications. The easiest way is to create an `.env`
file in the `src/` directory. Alternatively setting environment variables is
possible as well.

All the settings are optional. Keep in mind that when you choose a cache type
that you will need to set the corresponding cache settings for that type as well
(ex.: `REDIS_HOST`, `REDIS_PORT`, `REDIS_PASSWORD` or `REDIS_URL` is required
when using the **redis** type).

All the available options in an `.env` file:
```shell
# general
VERSION=1.0.0

# caching
CACHE=True
CACHE_TYPE=redis
CACHE_EXPIRATION=120

# redis
REDIS_HOST="your.redis.host.example.com"
REDIS_PORT=6379
REDIS_PASSWORD="YourRedisP@ssword!"

# OR, if your host provides a Connection URL 
# (see: https://redis-py.readthedocs.io/en/stable/#quickly-connecting-to-redis)
REDIS_URL="redis://YourUsername:YourRedisP@ssword!@your.redis.host.example.com:6379"

# logging
LOG_LEVEL=info
```

## Development

To develop locally start by creating a Python virtual environment and install the prerequisites:
```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

Run the Web Service (FastAPI) locally by running the FastAPI development server:
```bash
source .venv/bin/activate
cd src/
fastapi dev web.py
```
Now you can reach the SteamCMD API locally on [http://localhost:8000](http://localhost:8000).

Run the Job Service (Celery) locally by running celery directly:
```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
cd src/
celery -A job worker --loglevel=info --concurrency=2 --beat
```

### Black

To keep things simple, [Black](https://github.com/python/black) is used for code
style / formatting. Part of the pipeline will check if the code is properly
formatted according to Black code style. You can install it locally via pip:
```bash
pip install black
```
And then simply run it agains the Python source code:
```bash
black src
```
