[![pipeline status](https://gitlab.com/jonakoudijs/steamcmd-api/badges/master/pipeline.svg)](https://gitlab.com/jonakoudijs/steamcmd-api/commits/master)
[![code style black](https://img.shields.io/badge/code%20style-black-000000.svg)](https://github.com/python/black)
[![service status](https://img.shields.io/static/v1?label=service&message=status&color=blue)](https://status.steamcmd.net)

# SteamCMD API

Simple SteamCMD API

### Container Image

The API is run via a Docker image which contains both the `steamcmd` binary and the Python code which is wrapped around it.
You can build and run the container (locally) with Docker:
```
docker build -t steamcmd-api:test .
docker run -p 8080:8080 -d steamcmd-api:test -e "PORT=8080"
```
However using Docker Compose is preferred. See the [Development](#development) section for information.

### Deploying

The SteamCMD API is automatically deployed on Heroku when commits are done to/merged into master. This is done via the Gitlab pipeline.
If you want or need to deploy manually you will have to authenticate locally:
```
heroku container:login
```
And use the following deployment commands:
```
heroku container:push web --app steamcmd
heroku container:release web --app steamcmd
```

### Management

Management of the app is done mainly via the Heroku Dashboard. But some other services are used as well.
Timber.io is used for general logging and can be looked into by executing locally:
```
heroku addons:open timber-logging
```
Sentry.io is used for error logging / storing issues and can be looked into by executing locally:
```
heroku addons:open sentry
```

### Development

To keep it simple, [Black](https://github.com/python/black) is used for code style / formatting. Part of the pipeline
will check if the code is properly formatted according to Black code style. You can install it locally via pip:
```
pip install black
```
And then simply run it agains the Python source code:
```
black src
```
The easiest way to spin up the development environment is using Docker compose. This will build the image locally,
mount the correct directory (`src`) and set the required environment variables. Just execute compose up in the root:
```
docker-compose up
```
Now you can reach the SteamCMD API locally on [http://localhost:8080](http://localhost:8080)
