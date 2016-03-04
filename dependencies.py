#!/usr/bin/env python3
# download javascript dependencies

import sys
import os.path
import subprocess

dependencies = [
	(
		"jquery#~2.2.1",
		"bower_components/jquery/dist/jquery.min.js"
	),
	(
		"jquery-ui#~1.11.4",
		"bower_components/jquery-ui/jquery-ui.min.js"
	),
	(
		"undo-manager#~1.0.5",
		"bower_components/undo-manager/lib/undomanager.js"
	)
]

def resolve(dependencies=dependencies, basedir=sys.path[0]):
	for (name, filename) in dependencies:
		if not os.path.isfile(os.path.join(basedir, filename)):
			try:
				subprocess.check_call([ "bower", "install", name ], cwd=basedir)
			except Exception as e:
				print("Could not download %s (bower install %s)!" % (name, name), file=sys.stderr)
				print(e, file=sys.stderr)
				return False
	
	return True


if __name__ == "__main__":
	if not resolve():
		sys.exit(2)
