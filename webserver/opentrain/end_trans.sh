#!/bin/bash

rm -rf tmp-trans
python manage.py compilemessages
python manage.py compilejsi18n -l he -d django -o tmp-trans/jsi18n




