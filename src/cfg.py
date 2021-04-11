#!/usr/bin/env python3
"""
SteamCMD API global configuration.
"""

# allowed HTTP methods
ALLOWED_METHODS = ["GET", "HEAD", "OPTIONS"]

# allowed api version
ALLOWED_VERSIONS = ["v1"]

# available endpoints
AVAILABLE_ENDPOINTS = ["info", "version"]

# default cache expiration (seconds)
CACHE_EXPIRATION = 60

# default redis port
REDIS_DEFAULT_PORT = 6379

# default redis ssl
REDIS_DEFAULT_SSL = False

# default redis timeout (seconds)
REDIS_DEFAULT_TIMEOUT = 3

# file containing version
VERSION_FILE = ".version"
