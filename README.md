# SteamCMD API

Simple SteamCMD API


### Container Image

The API is run via a Docker image which contains both the `steamcmd` binary and the Python code which is wrapped around it.
To run the container you will have supply a port as well. For example:
```
docker run -ti -p 8080:8080 steamcmd-api:latest
```

### Deploying

The SteamCMD API is automatically deployed on Google AppEngine when commits are done to/merged into master. This is done via the Gitlab pipeline.
If you want or need to deploy manually you will have to authenticate locally and use the following deployment commands:
```
gcloud app deploy --project steamcmd
```
