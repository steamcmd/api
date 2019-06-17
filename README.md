# SteamCMD API

Simple SteamCMD API

### Container Image

The API is run via a Docker image which contains both the `steamcmd` binary and the Python code which is wrapped around it.
To locally build and test the container (locally) with Docker:
```
docker build -t steamcmd-api:test
docker run -p 8080:8080 -ti steamcmd-api:test -e "PORT=8080"
```

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
Timber.io is used for logging and can be looked into by executing locally:
```
heroku addons:open timber-logging
```

### Development

The easiest way to spin up the development environment is using Docker compose. This will build the image locally,
mount the correct directory (`src`) and set the required environment variables. Just execute compose up in the root:
```
docker-compose up
```
Now you can reach the SteamCMD API locally on [http://localhost:8080](http://localhost:8080)
