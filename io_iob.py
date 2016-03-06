import os
import os.path
import stat
import json
from glob import glob
import contextlib
import tempfile

@contextlib.contextmanager
def safe_open_w(filename, prefix=".~", suffix=".tmp"):
	mode = stat.S_IMODE(os.stat(filename).st_mode) if os.path.exists(filename) else None
	directory = os.path.dirname(filename)
	(fd, tmp) = tempfile.mkstemp(prefix="%s%s" % (prefix, os.path.basename(filename)), suffix=suffix, dir=directory)
	try:
		with os.fdopen(fd, 'w') as f:
			yield f
		os.rename(tmp, filename)
		tmp = None
		if mode is not None:
			os.chmod(filename, mode)
	finally:
		if tmp is not None:
			try:
				os.unlink(tmp)
			except:
				pass


class IobIo(object):
	def __init__(self, directory):
		self.directory = directory
		
		# tag_definitions: [ [ tag_id, tag_human_readable, tag_color ] ]
		with open(os.path.join(self.directory, "tag-definitions.json")) as f:
			self.tag_definitions = json.load(f)
		
		# segments: [ segment_id ]
		self.segments = list(map(
			lambda x: os.path.basename(x[:-4]),
			glob(os.path.join(self.directory, "*.txt"))
		))
		self.segments.sort()
		
		# tokens: { segment_id: [ token ] }
		self.tokens = {}
		
		# tags: { segment_id: { (tag, start, end) } }
		self._read_tags()
	
	
	def _read_tags(self):
		self.tags = {}
		for segment in self.segments:
			self.tags[segment] = set()
			
			filename = os.path.join(self.directory, "%s.tag" % segment)
			if not os.path.exists(filename) or not os.path.isfile(filename):
				return []
			
			with open(os.path.join(self.directory, "%s.tag" % segment)) as f:
				start = [-1] * len(self.tag_definitions)
				
				i = -1
				for line in f.readlines():
					i += 1
					
					l = line.strip().split()
					if len(l) != len(self.tag_definitions) + 1:
						raise Exception("Invalid line in tag file »%s«: »%s«" % (filename, line.strip()))
					
					l = l[1:]
					for j in range(len(l)):
						if len(l[j]) > 1:
							if l[j][2:] != self.tag_definitions[j][0]:
								raise Exception("Bad tag »%s« in line %s of file »%s«." % (l[j], i+1, filename))
						
						if start[j] >= 0 and not l[j].startswith("I-"):
							self.tags[segment].add((j, start[j], i-1))
							start[j] = -1
						
						if l[j].startswith("B-"):
							start[j] = i
			
				for j in range(len(start)):
					if start[j] >= 0:
						self.tags[segment].add((j, start[j], i))
				
			
			
	
	
	def _write_tags(self, segment):
		if not segment in self.segments:
			raise Exception("Unknown segment: »%s«" % segment)
		
		tokens = self.get_tokens(segment)
		tags = self.tags.get(segment, [])
		
		# this is not very efficient (but we have small files)
		with safe_open_w(os.path.join(self.directory, "%s.tag" % segment)) as f:
			for (i, token) in zip(range(len(tokens)), tokens):
				f.write(token)
				for (tag_index, tag_def) in zip(range(len(self.tag_definitions)), self.tag_definitions):
					tag_id = tag_def[0]
					out = "O"
					for (t,s,e) in tags:
						if t == tag_index and i == s:
							out = "B-%s" % tag_id
							break
						elif t == tag_index and s < i <= e:
							out = "I-%s" % tag_id
							break
					
					f.write(" ")
					f.write(out)
				
				f.write("\n")
		
	
	
	def _read_tokens(self, segment):
		with open(os.path.join(self.directory, "%s.txt" % segment)) as f:
			return list(map(
				lambda x: x.strip(),
				f.readlines()
			))
	
	
	def get_tag_definitions(self):
		return list(map(
			lambda x: (x[1], x[2]),
			self.tag_definitions
		))
	
	
	def get_segments(self):
		return self.segments
	
	
	def get_tokens(self, segment):
		if not segment in self.segments:
			raise Exception("Unknown segment: »%s«" % segment)
		
		if not segment in self.tokens:
			self.tokens[segment] = self._read_tokens(segment)
		
		return self.tokens[segment]
	
	
	def get_tags(self, segment):
		return list(self.tags.get(segment, []))
	
	
	def set_tag(self, segment, tag, start, end):
		if not segment in self.segments:
			raise Exception("Unknown segment: »%s«" % segment)
		
		tag = int(tag)
		start = int(start)
		end = int(end)
		
		if not (0 <= tag < len(self.tag_definitions)):
			raise Exception("Bad tag id: »%s«" % tag)
		
		tokens = self.get_tokens(segment)
		if end < start or not (0 <= start < len(tokens)) or not (0 <= end < len(tokens)):
			raise Exception("Bad token indices!")
		
		if not segment in self.tags:
			self.tags[segment] = set()
		
		self.tags[segment].add((tag, start, end))
		self._write_tags(segment)
	
	
	def remove_tag(self, segment, tag, start, end):
		tag = int(tag)
		start = int(start)
		end = int(end)
		
		if segment in self.tags:
			self.tags[segment].remove((tag, start, end))
		
		self._write_tags(segment)
	
	
	def clear_tags(self, segment):
		if segment in self.tags:
			self.tags[segment].clear()
		
		self._write_tags(segment)
