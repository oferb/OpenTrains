#!/bin/sh

cd %(HOME)s/work/OpenTrains/webserver/opentrain
exec gunicorn -p %(HOME)s/opentrain.id \
    -b 127.0.0.1:9000 \
    -w 2 opentrain.wsgi:application
 
