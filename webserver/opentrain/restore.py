#! /usr/bin/env python

import os
os.environ['DJANGO_SETTINGS_MODULE']='opentrain.settings'
import reports.logic
reports.logic.restore_reports('/tmp/backup.gz')









