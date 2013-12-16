import json
import models
from bottle import route, run, abort, static_file,template
from bottle import request, get, post, redirect, default_app, response,HTTPResponse
from google.appengine.ext import db

def raise_error(msg):
	body = json.dumps(dict(error=msg))
	print body
	raise HTTPResponse(status=400,
					body=body, Content_Type='application/json');

def guard(func):
	def _wrap(*args,**kwargs):
		try:
			res = func(*args,**kwargs)
		except HTTPResponse,h:
			raise h
		except Exception,e:
			raise_error(unicode(e))
		return res
	return _wrap

@post('/reports/add/')
@guard
def add_reports():
    body = request.body.read()
    text = json.dumps(json.loads(body))
    rep = models.RawReport(text=text)
    rep.save()
    response.status = 201
    
@get('/')
@guard
def home():
	return get_reports()


@get('/reports/get/')
@guard
def get_reports():
	q = db.GqlQuery("SELECT * FROM RawReport order by timestamp DESC")
	rrs = []
	for rr in q:
		rrs.append(rr)
	print len(rrs)
	return template('results.html', rrs=rrs)

app = default_app()




