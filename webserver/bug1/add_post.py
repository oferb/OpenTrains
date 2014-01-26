#!/usr/bin/env python
import requests
import json
import time
import sys

def main(count,sleep):
	print 'count = %d sleep = %d' % (count,sleep)
	fh = open('item.json')
	body = json.load(fh)
	fh.close()
	headers = {'content-type':'application/json'}
	for i in xrange(count):
		print '%d/%d' % (i,count)
		resp = requests.post('http://localhost:8000/reports/add/',headers=headers,data=body)
		print resp
		time.sleep(sleep)

if __name__ == '__main__':
	if len(sys.argv) >= 2:
		count = int(sys.argv[1])
	else:
		count = 1
	if len(sys.argv) == 3:
		sleep = float(sys.argv[2])
	else:
		sleep = 10
	main(count,sleep)


