from configparser import RawConfigParser

import os
import logging

INIFILE = "cfgslicer.ini"

class Settings:
	def __init__(self, folder):
		self.root = "C:\\Users\\jeff\\AppData\\Roaming\\PrusaSlicer"
		self.attrFile = "attributes.json"
				
		self.inifile = os.path.join(folder, INIFILE)
		logging.info("Loading inifile (%s)" % self.inifile)
		
		cfg = RawConfigParser()
		with open(self.inifile) as stream:
			cfg.read_string("[top]\n" + stream.read())

		for opt, value in cfg.items("top"):
			if opt == "root":
				self.root = value
			elif opt == "attributefile":
				self.attrFile = value
			else:
				logging.info("ignoring option, value (%s) (%s)" % (opt, value))
				
		logging.debug("settings: root = (%s)" % self.root)
		logging.debug("settings: attrfile = (%s)" % self.attrFile)
					
	def save(self):
		try:		
			cfp = open(self.inifile, 'w')
		except:
			logging.error("Unable to open settings file (%s) for writing" % self.inifile)
			return
		
		cfp.write("root = %s\n" % self.root)
		cfp.write("attributefile = %s\n" % self.attrFile)
		cfp.close()
