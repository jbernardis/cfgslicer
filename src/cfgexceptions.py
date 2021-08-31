class CfgUnknownCategory(Exception):
	def __init__(self, category):
		self.category = category

class CfgUnknownFile(Exception):
	def __init__(self, filename):
		self.filename = filename

class CfgUnknownAttribute(Exception):
	def __init__(self, attribute):
		self.attribute = attribute
