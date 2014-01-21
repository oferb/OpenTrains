#!/usr/bin/env python
import requests
import json
import time
import sys

def main(count):
	fh = open('item.json')
	body = json.load(fh)
	fh.close()
	headers = {'content-type':'application/json'}
	for i in xrange(count):
		print '%d/%d' % (i,count)
		resp = requests.post('http://localhost:8000/reports/add/',headers=headers,data=body)
		print resp
		time.sleep(10)

if __name__ == '__main__':
	if len(sys.argv) == 2:
		count = int(sys.argv[1])
	else:
		count = 1
	main(count)


