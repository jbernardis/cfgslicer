import os
import datetime
from configparser import RawConfigParser

from cfgexceptions import *

class CfgFile:
	def __init__(self, attrdict):
		self.modified = False
		self.attributes = attrdict
		
	def setModified(self, flag=True):
		self.modified = flag
		
	def isModified(self):
		return self.modified
		
	def getAttributes(self):
		return self.attributes
	
	def getAttribute(self, name):
		try:
			return self.attributes[name]
		except KeyError:
			raise CfgUnknownAttribute(name)
	
	def setAttribute(self, name, value, mustExist=False):
		if mustExist:
			if name not in self.attributes:
				raise CfgUnknownAttribute(name)
			
		self.attributes[name] = value
		self.setModified()
	
	
class CfgSlicer:	
	def __init__(self, root, dirs):
		self.root = root
		self.dirs = dirs
		self.loadAttributes()
		
	def loadAttributes(self):
		self.fileMap = {}
		for d in self.dirs:
			path = os.path.join(self.root, d)
			fl = [os.path.join(path, f) for f in os.listdir(path) if os.path.isfile(os.path.join(path, f)) and f.endswith(".ini")]

			fm = {}
			for fp in fl:
				parser = RawConfigParser()
				with open(fp) as stream:
					parser.read_string("[top]\n" + stream.read())

				fa = {}					
				for k, v in parser.items("top"):
					fa[k] = v
				fm[os.path.basename(fp)] = CfgFile(fa)
				
			self.fileMap[d] = fm	
			
	def isAnyModified(self):
		for cat in self.fileMap:
			for f in self.fileMap[cat]:
				if self.fileMap[cat][f].isModified():
					print("modified: %s %s" % (cat, f))
					return True
				
		return False
	
	def writeProperties(self, cat, fn):
		if cat not in self.fileMap:
			raise CfgUnknownCategory(cat)
		
		if fn not in self.fileMap[cat]:
			raise CfgUnknownFile(fn)
				
		fqn = os.path.join(self.root, cat, fn)
		attrdict = self.fileMap[cat][fn].getAttributes()
		
		with open(fqn, "w") as ofp:
			dt = datetime.datetime.now()
			tstamp = dt.strftime("%Y-%m-%d %H:%M:%S")
	
			ofp.write("# generated by CfgSlicer on %s\n" % tstamp)
	
			for k in sorted(attrdict.keys()):
				ofp.write("%s = %s\n" % (k, attrdict[k]))
				
		self.fileMap[cat][fn].setModified(False)
		
	def writeModified(self):
		for cat in self.fileMap:
			for f in self.fileMap[cat]:
				if self.fileMap[cat][f].isModified():
					print("writing modified: %s %s" % (cat, f))
					self.writeProperties(cat, f)
	
	def getAttribute(self, cat, fn, name):
		if cat not in self.fileMap:
			raise CfgUnknownCategory(cat)
		
		if fn not in self.fileMap[cat]:
			raise CfgUnknownFile(fn)
				
		return self.fileMap[cat][fn].getAttribute(name)
	
	def getAttributes(self, cat, fn):
		if cat not in self.fileMap:
			raise CfgUnknownCategory(cat)
		
		if fn not in self.fileMap[cat]:
			raise CfgUnknownFile(fn)
				
		return self.fileMap[cat][fn].getAttributes()
	
	def setAttribute(self, cat, fn, name, value, mustExist=False):
		if cat not in self.fileMap:
			raise CfgUnknownCategory(cat)
		
		if fn not in self.fileMap[cat]:
			raise CfgUnknownFile(fn)
		
		self.fileMap[cat][fn].setAttribute(name, value, mustExist)
		
	def getFileList(self, cat):
		if cat not in self.fileMap:
			raise CfgUnknownCategory(cat)
		
		return list(self.fileMap[cat].keys())
		
		
