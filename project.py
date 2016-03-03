import os
import os.path
import json

class Project(object):
	def __init__(self, directory):
		with open(os.path.join(directory, "tokens.txt")) as f:
			self.tokens = [ x.strip() for x in f.readlines() ]
		
		with open(os.path.join(directory, "tag-definitions.json")) as f:
			self.tag_definitions = json.loads("".join(f.readlines()))
		
		

if __name__ == "__main__":
	p = Project("test-project")
	print(p.tokens)
	print(p.tags)
