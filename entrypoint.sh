#!/bin/sh

supervisord -c /etc/supervisord.conf &

gunicorn -w 12 "app:app" -b 0.0.0.0:8000
