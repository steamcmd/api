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

# sentry.io configuration
SENTRY_SDK_URL = "https://c38d9620b2da45d086ac403a7e59946b@sentry.io/1486480"

# file containing version
VERSION_FILE = ".version"
