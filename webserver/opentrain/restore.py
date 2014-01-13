#! /usr/bin/env python

import os
os.environ['DJANGO_SETTINGS_MODULE']='opentrain.settings'

def main():
    import reports.logic
    import analysis.logic
    reports.logic.restore_reports('/tmp/backup.gz')
    analysis.logic.analyze_raw_reports()

if __name__ == '__main__':
    main()









