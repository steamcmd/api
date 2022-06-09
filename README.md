[![Build Status](https://img.shields.io/github/workflow/status/steamcmd/api/Deploy.svg?logo=github)](https://github.com/steamcmd/api/actions)
[![Snyk Vulnerabilities](https://snyk.io/test/github/steamcmd/api/badge.svg?targetFile=requirements.txt)](https://snyk.io/test/github/steamcmd/api)
[![CodeFactor](https://www.codefactor.io/repository/github/steamcmd/api/badge)](https://www.codefactor.io/repository/github/steamcmd/api)
[![Code Style](https://img.shields.io/badge/code%20style-black-000000.svg)](https://github.com/python/black)
[![Discord Online](https://img.shields.io/discord/928592378711912488.svg)](https://discord.steamcmd.net)
[![Service Status](https://img.shields.io/static/v1?label=service&message=status&color=blue)](https://status.steamcmd.net)
[![Image Size](https://img.shields.io/docker/image-size/steamcmd/api/latest.svg)](https://hub.docker.com/r/steamcmd/api)
[![MIT License](https://img.shields.io/badge/license-MIT-blue.svg)](LICENSE)
[![GitHub Release](https://img.shields.io/github/v/release/steamcmd/api?label=version)](https://github.com/steamcmd/api/releases)

# SteamCMD API

Read-only API interface for steamcmd app_info

### Container

The API is run via a Docker image which contains both the `steamcmd` binary and
the Python code which is wrapped around it. You can build and run the container
(locally) with Docker:
```
docker build -t steamcmd-api:test .
docker run -p 8080:8080 -d steamcmd-api:test
```
However during development, using Docker Compose is preferred.
See the [Development](#development) section for information.

### Hosting

Newer versions of the API are automatically deployed on Azure when a new version
has been created on Github, see the [deploy workflow](.github/workflows/deploy.yml).
Deployment is done via [Github Actions](https://github.com/steamcmd/api/actions).

Deploying to Heroku can be done to easily host it yourself. First authenticate
locally with the `heroku` cli:
```
heroku container:login
```
Then use the following deployment commands:
```
heroku container:push web --app yourappname
heroku container:release web --app yourappname
```

### Development

The easiest way to spin up the development environment is using Docker compose.
This will build the image locally, mount the correct directory (`src`) and set
the required environment variables. If you are on windows you should store the
repository in the WSL filesystem or it will fail. Execute compose up in the root:
```
docker-compose up
```
Now you can reach the SteamCMD API locally on [http://localhost:8080](http://localhost:8080)

To keep things simple, [Black](https://github.com/python/black) is used for code style / formatting. Part of the pipeline
will check if the code is properly formatted according to Black code style. You can install it locally via pip:
```
pip install black
```
And then simply run it agains the Python source code:
```
black src
```
