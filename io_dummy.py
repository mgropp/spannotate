class DummyIo(object):
	def __init__(self):
		self.tags = {
			"105": [],
			"106": []
		}
	
	
	def get_tag_definitions(self):
		return [
			[ "Location: City",    "#4600C4" ],
			[ "Location: Country", "#E82200" ],
			[ "Person: Title",     "#FFD500" ],
			[ "Person: Name",      "#81FF00" ]
		]
	
	
	def get_segments(self):
		return [ "105", "106" ]
	
	
	def get_tokens(self, segment):
		if str(segment) == "105":
			return [ "Lorem", "ipsum", "dolor", "sit", "amet", ",", "consectetur", "adipiscing", "elit", ",", "sed", "do", "eiusmod", "tempor", "incididunt", "ut", "labore", "et", "dolore", "magna", "aliqua", ".", "Ut", "enim", "ad", "minim", "veniam", ",", "quis", "nostrud", "exercitation", "ullamco", "laboris", "nisi", "ut", "aliquip", "ex", "ea", "commodo", "consequat", ".", "Duis", "aute", "irure", "dolor", "in", "reprehenderit", "in", "voluptate", "velit", "esse", "cillum", "dolore", "eu", "fugiat", "nulla", "pariatur", ".", "Excepteur", "sint", "occaecat", "cupidatat", "non", "proident", ",", "sunt", "in", "culpa", "qui", "officia", "deserunt", "mollit", "anim", "id", "est", "laborum", "." ]
		elif str(segment) == "106":
			return [ "Praesent", "et", "mi", "vitae", "libero", "tristique", "feugiat", ".", "Pellentesque", "habitant", "morbi", "tristique", "senectus", "et", "netus", "et", "malesuada", "fames", "ac", "turpis", "egestas", ".", "Sed", "vel", "dignissim", "justo", ".", "Mauris", "venenatis", "sem", "in", "varius", "vestibulum", ".", "Interdum", "et", "malesuada", "fames", "ac", "ante", "ipsum", "primis", "in", "faucibus", ".", "Suspendisse", "massa", "dolor", ",", "tincidunt", "ut", "dictum", "vitae", ",", "semper", "et", "lectus", ".", "Etiam", "condimentum", "laoreet", "elit", ",", "non", "elementum", "dui", "lacinia", "vitae", ".", "Etiam", "porta", "sapien", "odio", ",", "interdum", "convallis", "dui", "laoreet", "quis", ".", "Nam", "vitae", "hendrerit", "risus", ",", "ut", "elementum", "mi", ".", "Aliquam", "consequat", "finibus", "sapien", "non", "condimentum", ".", "Vivamus", "sit", "amet", "consectetur", "purus", ".", "Quisque", "vitae", "lorem", "pellentesque", ",", "convallis", "ex", "ut", ",", "eleifend", "lacus", ".", "Morbi", "suscipit", "eu", "nulla", "eu", "dictum", ".", "Donec", "cursus", "purus", "ex", ".", "Suspendisse", "finibus", "consectetur", "ante", ",", "et", "efficitur", "lectus", "." ]
		
		raise Exception("Unknown segment.")
	
	
	def get_tags(self, segment):
		return self.tags[str(segment)]
	
	
	def set_tag(self, segment, tag, start, end):
		taglist = self.tags[str(segment)]
		if not (start, end, tag) in taglist:
			taglist.append((tag, start, end))
	
	
	def remove_tag(self, segment, tag, start, end):
		taglist = self.tags[str(segment)]
		taglist.remove((tag, start, end))
	
	
	def clear_tags(self, segment):
		self.tags[str(segment)] = []
