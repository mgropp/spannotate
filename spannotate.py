#!/usr/bin/env python3
import sys
import os.path
import webbrowser

import dependencies
import server

from config import port

if __name__ == "__main__":
	if len(sys.argv) < 2:
		print("Missing argument! %s <annotation directory>" % sys.argv[0], file=sys.stderr)
		sys.exit(1)
	
	server_dir = os.path.abspath(os.path.dirname(sys.argv[0]))
	project_dir = sys.argv[1]
	
	if not dependencies.resolve(server_dir):
		sys.exit(2)
	
	webbrowser.open("http://localhost:%d" % port)
	server.serve(server_dir, project_dir)
	
