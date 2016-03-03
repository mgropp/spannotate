#!/usr/bin/env python3
import sys
import os.path
import urllib
import json
import mimetypes
import logging
from wsgiref.simple_server import make_server

from config import host
from config import port

# from io_dummy import DummyIo
from io_iob import IobIo

if len(sys.argv) < 2:
	print("Missing argument! %s <annotation directory>" % sys.argv[0], file=sys.stderr)
	sys.exit(1)

io = IobIo(sys.argv[1])
# io = DummyIo()

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

mimetypes.init()
server_dir = os.path.abspath(os.path.dirname(sys.argv[0]))

unquote_plus = urllib.unquote_plus if hasattr(urllib, 'unquote_plus') else urllib.parse.unquote_plus

def error_message(message, start_response):
	start_response(message, [('Content-Type', 'text/plain; charset=utf-8')])
	return [message.encode('utf-8')]


def file_wrapper(filename, block_size):
	with open(filename, 'rb') as f:
		buf = f.read(block_size)
		while len(buf) > 0:
			yield buf
			buf = f.read(block_size)


def serve_file(path, env, start_response, server_dir=server_dir, block_size=8192):
	if path[0] == '/':
		path = path[1:]
	
	abspath = os.path.abspath(os.path.relpath(path, server_dir))
	if os.path.commonprefix([abspath, server_dir]) != server_dir:
		return error_message('403 Access denied.', start_response)
	
	if not os.path.exists(path):
		return error_message('404 Not found.', start_response)
	
	start_response(
		'200 OK.',
		[
			('Content-Type', mimetypes.types_map.get(os.path.splitext(abspath)[1], 'application/octet-stream')),
			('Content-Length', str(os.stat(abspath).st_size))
		]
	)
	
	if not 'wsgi.file_wrapper' in env:
		f = open(abspath, 'rb')
		return env['wsgi.file_wrapper'](f, block_size)
	else:
		return file_wrapper(abspath, block_size)


def app(env, start_response):
	path = env['PATH_INFO']
	query_str = env.get('QUERY_STRING' ,'')
	
	if path == '/' and len(query_str) > 0:
		args = dict(map(lambda y: (unquote_plus(y[0]), unquote_plus(y[1])), map(lambda x: tuple(x.split('=', 1)), query_str.split('&'))))
	
		action = args.get('action', None)
		if action == 'get_tag_definitions':
			try:
				tag_definitions = io.get_tag_definitions()
			except Exception as e:
				logger.critical("%s: %s" % (type(e).__name__, e))
				return error_message('422 Bad parameters.', start_response)
			
			start_response('200 OK.', [ ('Content-Type', 'application/json') ])
			return [ json.dumps(tag_definitions).encode('utf-8') ]
		
		elif action == 'get_segments':
			try:
				segments = io.get_segments()
			except Exception as e:
				logger.critical("%s: %s" % (type(e).__name__, e))
				return error_message('422 Bad parameters.', start_response)
			
			start_response('200 OK.', [ ('Content-Type', 'application/json') ])
			return [ json.dumps(segments).encode('utf-8') ]
		
		elif action == 'get_tokens':
			segment = args.get("segment", None)
			if segment is None:
				return error_message('422 Bad parameters.', start_response)
			
			try:
				tokens = io.get_tokens(segment)
			except Exception as e:
				logger.critical("%s: %s" % (type(e).__name__, e))
				return error_message('422 Bad parameters.', start_response)
			
			start_response('200 OK.', [ ('Content-Type', 'application/json') ])
			return [ json.dumps(tokens).encode('utf-8') ]
		
		elif action == "get_tags":
			segment = args.get("segment", None)
			if segment is None:
				return error_message('422 Bad parameters.', start_response)
			
			try:
				tags = io.get_tags(segment)
			except Exception as e:
				logger.critical("%s: %s" % (type(e).__name__, e))
				return error_message('422 Bad parameters.', start_response)
			
			start_response('200 OK.', [ ('Content-Type', 'application/json') ])
			return [ json.dumps(tags).encode('utf-8') ]
		
		elif action == "set_tag":
			segment = args.get("segment", None)
			tag = args.get("tag", None)
			start = args.get("start", None)
			end = args.get("end", None)
			
			if segment is None or tag is None or start is None or end is None:
				return error_message('422 Bad parameters.', start_response)
			
			try:
				io.set_tag(segment, tag, start, end)
			except Exception as e:
				logger.critical("%s: %s" % (type(e).__name__, e))
				return error_message('422 Bad parameters.', start_response)
			
			start_response('200 OK.', [ ('Content-Type', 'text/plain') ])
			return [ "OK".encode('utf-8') ]
		
		elif action == "remove_tag":
			segment = args.get("segment", None)
			tag = args.get("tag", None)
			start = args.get("start", None)
			end = args.get("end", None)
			
			try:
				io.remove_tag(segment, tag, start, end)
			except Exception as e:
				logger.critical("%s: %s" % (type(e).__name__, e))
				return error_message('422 Bad parameters.', start_response)
			
			start_response('200 OK.', [ ('Content-Type', 'text/plain') ])
			return [ "OK".encode('utf-8') ]
		
		else:
			return error_message('422 Bad parameters.', start_response)
	else:
		if path == '' or path == '/':
			path = '/index.html'
		return serve_file(path, env, start_response)


if not os.path.isfile(os.path.join(sys.path[0], "bower_components/jquery/dist/jquery.min.js")):
	import subprocess
	try:
		subprocess.check_call([ "bower", "install", "jquery#~2.2.1" ], cwd=sys.path[0])
	except Exception as e:
		print("Could not download jquery (bower install jquery)!", file=sys.stderr)
		print(e, file=sys.stderr)
		sys.exit(2)


server = make_server(host, port, app)
print('Serving HTTP on %sport %d...' % ('' if host == '' else '%s, ' % host, port))
server.serve_forever()
