[![Build Status](https://github.com/steamcmd/api/actions/workflows/deploy.yml/badge.svg)](https://github.com/steamcmd/api/actions)
[![CodeFactor](https://www.codefactor.io/repository/github/steamcmd/api/badge)](https://www.codefactor.io/repository/github/steamcmd/api)
[![Code Style](https://img.shields.io/badge/code%20style-black-000000.svg)](https://github.com/python/black)
[![Discord Online](https://img.shields.io/discord/928592378711912488.svg)](https://discord.steamcmd.net)
[![Service status](https://img.shields.io/uptimerobot/status/m782827237-5067fd1d69e3b1b2e4e40fff)](https://status.steamcmd.net)
[![Image Size](https://img.shields.io/docker/image-size/steamcmd/api/latest.svg)](https://hub.docker.com/r/steamcmd/api)
[![GitHub Release](https://img.shields.io/github/v/release/steamcmd/api?label=version)](https://github.com/steamcmd/api/releases)
[![GitHub Sponsors](https://img.shields.io/github/sponsors/steamcmd)](https://github.com/sponsors/steamcmd)
[![MIT License](https://img.shields.io/badge/license-MIT-blue.svg)](LICENSE)

# SteamCMD API

Read-only API interface for steamcmd app_info. Updates of the API are
automatically deployed on Deta via [Github Actions](https://github.com/steamcmd/api/actions)
when a new version has been created on Github.

## Self-hosting

The easiest way to host the API yourself is using the free cloud platform
[Deta](https://www.deta.sh). Install the CLI according to the documentation:
[https://docs.deta.sh/docs/cli/install](https://docs.deta.sh/docs/cli/install).

After installing authenticate locally with the `deta` cli:
```
deta login
```
Then use the deploy command:
```
cd src/
deta deploy
```

## Container

The API can easily be run via a Docker image which contains the API code and the
`uvicorn` tool to be able to respond to web requests. With every new version of
the API the Docker images is automatically rebuild and pushed to the Docker Hub:
```
docker pull steamcmd/api:latest
```
```
docker pull steamcmd/api:1.10.0
```
```
docker run -p 8000:8000 -d steamcmd/api:latest
```
However during development, using Docker Compose is preferred. See the
[Development](#development) section for information.

## Configuration

When hosting the API yourself there are few settings you can change to configure
the API to your platform specifications. The easiest way is to create an `.env`
file in the `src/` directory. Alternatively setting environment variables is
possible as well.

All the settings are optional. Keep in mind that when you choose a cache type
that you will need to set the corresponding cache settings for that type as well
(ex.: `REDIS_HOST`, `REDIS_PORT`, `REDIS_PASSWORD` is required when using the
**redis** type).

All the available options in an `.env` file:
```
# general
VERSION=1.0.0

# caching
CACHE=True
CACHE_TYPE=deta
CACHE_EXPIRATION=120

# redis
REDIS_HOST="your.redis.host.example.com"
REDIS_PORT=18516
REDIS_PASSWORD="YourRedisP@ssword!"

# deta
DETA_BASE_NAME="steamcmd"
DETA_PROJECT_KEY="YourDet@ProjectKey!"
```

## Development

Run the api locally by installing a web server like uvicorn and running it:
```
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
pip install uvicorn
cd src/
uvicorn main:app --reload
```

The easiest way to spin up the development environment is using Docker compose.
This will build the image locally, mount the correct directory (`src`) and set
the required environment variables. If you are on windows you should store the
repository in the WSL filesystem or it will fail. Execute compose up in the root:
```
docker compose up
```
Now you can reach the SteamCMD API locally on [http://localhost:8080](http://localhost:8080).

### Black

To keep things simple, [Black](https://github.com/python/black) is used for code
style / formatting. Part of the pipeline will check if the code is properly
formatted according to Black code style. You can install it locally via pip:
```
pip install black
```
And then simply run it agains the Python source code:
```
black src
```
