import json

STRINGTYPE = "string"
LONGSTRINGTYPE = "longstring"
COLORTYPE = "color"
HIDDEN = "hidden"
BOOLEAN = "boolean"

INFILLTYPE = "infill"
SHELLINFILLTYPE = "shellinfill"
SUPPORTINFILLTYPE = "supportinfill"
IRONINGTYPE = "ironing"
SEAMPOSTYPE = "seamposition"
LIMITSUSAGE = "limitsusage"
ENSUREVERTICALSHELL = "ensureverticalshell"


class AttributeMap:
	def __init__(self, fn):
		self.attrFileName = fn
		self.extGroup = None
		self.extAttr = []
		with open(fn, "r") as fp:
			self.attrMap = json.load(fp)

		for c in self.attrMap["categories"]:
			for grp in self.attrMap[c]["groups"]:
				for a in self.attrMap[c][grp]:
					if "subgroup" not in a:
						try:
							a["label"]
						except KeyError:
							a["label"] = a["name"]

						try:
							a["type"]
						except KeyError:
							a["type"] = STRINGTYPE
						
		self.extCategory = self.attrMap["extruders"]["category"]
		self.extGroup = self.attrMap["extruders"]["group"]
		self.extAttr = [x["name"] for x in self.attrMap[self.extCategory][self.extGroup] if "name" in x]
		try:
			self.attrVersion = self.attrMap["version"]
		except KeyError:
			self.attrVersion = "Unknown"

	def updateAttributeVersion(self, newVersion):
		with open(self.attrFileName, "r") as fp:
			attr = json.load(fp)
		attr["version"] = newVersion
		with open(self.attrFileName, "w") as fp:
			json.dump(attr, fp, indent=4)

	def getAttributeVersion(self):
		return self.attrVersion
			
	def getCategories(self):
		return self.attrMap["categories"]
	
	def getGroups(self, cat):
		return self.attrMap[cat]["groups"]
	
	def getGroupAttrs(self, cat, grp):
		return self.attrMap[cat][grp]
	
	def getExtruderCategory(self):
		return self.extCategory
	
	def getExtruderGroup(self):
		return self.extGroup
	
	def isExtruderCategory(self, cat):
		return cat == self.extCategory
	
	def isExtruderGroup(self, cat, grp):
		if cat != self.extCategory:
			return False

		if grp != self.extGroup:		
			return False
		
		return True
	
	def isExtruderAttribute(self, cat, name):
		if self.extGroup not in self.attrMap[cat]:
			return False
		
		return name in self.extAttr
		
	def getSingleAttribute(self, cat, name):
		al = self.getCatAttrs(cat)
		for a in al:
			if "subgroup" in a:
				continue

			if a["name"] == name:
				return a
			
		return None
	
	def getCatAttrs(self, cat):
		attrList = []	
		for grp in self.attrMap[cat]["groups"]:
			attrList.extend(self.attrMap[cat][grp])
		return attrList
	
	def getChoices(self, ctype):
		return self.attrMap["choicetypes"][ctype]

	def getChoiceTypes(self):
		return self.attrMap["choicetypes"].keys()

	def IsChoiceType(self, ctype):
		return ctype in self.attrMap["choicetypes"]

	def __call__(self, cat):
		self.iterCat = cat
		return self
			
	def __iter__(self):
		self.attrList = []	
		for grp in self.attrMap[self.iterCat]["groups"]:
			self.attrList.extend(self.attrMap[self.iterCat][grp])
		self.attrx = 0
		return self
	
	def __next__(self):
		if self.attrx >= len(self.attrList):
			raise StopIteration
		
		rv = self.attrList[self.attrx]
		self.attrx += 1
		
		return rv
	