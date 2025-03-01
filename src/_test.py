#!/usr/bin/env python3

import redis

rds = redis.Redis(
    host="steamcmd-redis-svc",
    port=6379,
    password="4jch9e2w4xptUqCSTq8lnyX",
    db=0
)

# Initialize cursor
cursor = 0
false_apps = []

# Use SCAN to iterate through keys that start with "app."
while True:
    cursor, apps = rds.scan(cursor, match='app.*')
    for app in apps:
        # Check if the value of the app is "false"
        if rds.get(app) == b'false':
            app = app.decode("UTF-8")
            app = app.split(".")[1]
            false_apps.append(int(app))

    if cursor == 0:
        break

for app in false_apps:
    print(app)