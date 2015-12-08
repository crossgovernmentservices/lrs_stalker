#!/usr/bin/env bash

gunicorn -c gunicorn_config.py -b 0.0.0.0:$PORT application:app
