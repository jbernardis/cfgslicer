from cfgexceptions import CfgInvalidColor

def parseColorValue(pv):
	if pv is None:
		raise CfgInvalidColor
	
	if len(pv) != 7:
		raise CfgInvalidColor
	
	if pv[0] != '#':
		raise CfgInvalidColor
	
	try:
		int(pv[1:], 16)
	except ValueError:
		raise CfgInvalidColor	
	
	r = int(pv[1:3], 16)
	g = int(pv[3:5], 16)
	b = int(pv[5:7], 16)
	
	return r, g, b