import json

STRINGTYPE = "string"
LONGSTRINGTYPE = "longstring"
COLORTYPE = "color"
INFILLTYPE = "infill"
SHELLINFILLTYPE = "shellinfill"
SUPPORTINFILLTYPE = "supportinfill"
IRONINGTYPE = "ironing"
SEAMPOSTYPE = "seamposition"
LIMITSUSAGE = "limitsusage"
HIDDEN = "hidden"
BOOLEAN = "boolean"

class AttributeMap:
	def __init__(self, fn):		
		with open(fn, "r") as fp:
			self.attrMap = json.load(fp)

		for c in self.attrMap["categories"]:
			for grp in self.attrMap[c]["categories"]:
				for a in self.attrMap[c][grp]:
					try:
						a["label"]
					except KeyError:
						a["label"] = a["name"]
						
					try:
						a["type"]
					except KeyError:
						a["type"] = STRINGTYPE
			
	def getCategories(self):
		return self.attrMap["categories"]
	
	def getGroups(self, cat):
		return self.attrMap[cat]["categories"]
	
	def getGroupAttrs(self, cat, grp):
		return self.attrMap[cat][grp]
	
	def getSingleAttribute(self, cat, name):
		al = self.getCatAttrs(cat)
		for a in al:
			if a["name"] == name:
				return a
			
		return None
	
	def getCatAttrs(self, cat):
		attrList = []	
		for grp in self.attrMap[cat]["categories"]:
			attrList.extend(self.attrMap[cat][grp])
		return attrList
	
	def getChoices(self, ctype):
		return self.attrMap["choicetypes"][ctype]

	def __call__(self, cat):
		print("in call")
		self.iterCat = cat
		return self
			
	def __iter__(self):
		print("in iter, cat = (%s)" % self.iterCat)
		self.attrList = []	
		for grp in self.attrMap[self.iterCat]["categories"]:
			self.attrList.extend(self.attrMap[self.iterCat][grp])
		self.attrx = 0
		return self
	
	def __next__(self):
		if self.attrx >= len(self.attrList):
			raise StopIteration
		
		rv = self.attrList[self.attrx]
		self.attrx += 1
		
		return rv
	