#!/bin/sh
while true; do
    flask deploy
    if [[ "$?" == "0" ]]; then
        break
    fi
    echo Deploy command failed, retrying in 5 secs...
    sleep 5
done
exec gunicorn --bind unix:/tmp/SITENAME.socket --access-logfile - --error-logfile - run:app
