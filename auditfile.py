import os
import wx
from configparser import RawConfigParser


class AuditReport(wx.Dialog):
	def __init__(self, parent, cat, fn, new, missing, common):
		wx.Dialog.__init__(self, parent, wx.ID_ANY, "Audit Report for file %s/\"%s\"" % (cat, fn))
		self.parent = parent

		self.Bind(wx.EVT_CLOSE, self.onClose)
		
		vsizer = wx.BoxSizer(wx.VERTICAL)
		vsizer.AddSpacer(20)
		
		hsz = wx.BoxSizer(wx.HORIZONTAL)
		hsz.AddSpacer(20)	

		self.trReport = wx.TreeCtrl(self, wx.ID_ANY, size=(400, 400), style=wx.TR_HAS_BUTTONS | wx.TR_LINES_AT_ROOT | wx.TR_HIDE_ROOT | wx.TR_ROW_LINES)
		
		root = self.trReport.AddRoot("root")
		
		cfg = self.trReport.AppendItem(root, "Configured Attributes missing from file")
		for i in missing:
			self.trReport.AppendItem(cfg, i)
		
		cfg = self.trReport.AppendItem(root, "file attributes not in Configuration")
		for i in new:
			self.trReport.AppendItem(cfg, i)
		
		cfg = self.trReport.AppendItem(root, "Attributes common to both")
		for i in common:
			self.trReport.AppendItem(cfg, i)
			
		# self.trReport.ExpandAll()
		
		hsz.Add(self.trReport)
				
		hsz.AddSpacer(20)
		vsizer.Add(hsz)
		vsizer.AddSpacer(20)			
		
		self.SetSizer(vsizer)
		self.Fit()
	
	def onClose(self, _):
		self.EndModal(wx.ID_OK)


class AuditFileDlg(wx.Dialog):
	def __init__(self, parent, root, attrMap, cats):
		wx.Dialog.__init__(self, parent, wx.ID_ANY, "File Audit")
		self.parent = parent
		self.root = root
		self.attrMap = attrMap
		self.cats = cats

		self.Bind(wx.EVT_CLOSE, self.onExit)
		
		self.currentCategory = None
		self.currentFile = None
		
		vsizer = wx.BoxSizer(wx.VERTICAL)
		vsizer.AddSpacer(20)
		
		hsz = wx.BoxSizer(wx.HORIZONTAL)
		hsz.AddSpacer(20)				
		st = wx.StaticText(self, wx.ID_ANY, "Category:", size=(70, -1))
		hsz.Add(st, 0, wx.TOP, 4)
		hsz.AddSpacer(10)
		self.chCategory = wx.Choice(self, wx.ID_ANY, choices=self.cats)
		self.chCategory.SetSelection(0)
		self.currentCategory = self.cats[0]
		self.Bind(wx.EVT_CHOICE, self.onCategory, self.chCategory)
		hsz.Add(self.chCategory)
		hsz.AddSpacer(20)
		vsizer.Add(hsz)
		vsizer.AddSpacer(10)

		hsz = wx.BoxSizer(wx.HORIZONTAL)
		hsz.AddSpacer(20)				
		st = wx.StaticText(self, wx.ID_ANY, "File:", size=(70, -1))
		hsz.Add(st, 0, wx.TOP, 4)
		hsz.AddSpacer(10)

		self.bFile = wx.Button(self, wx.ID_ANY, "...", size=(20, -1))
		hsz.Add(self.bFile)
		self.Bind(wx.EVT_BUTTON, self.onbFile, self.bFile)
		
		hsz.AddSpacer(10)
		
		self.stFile = wx.StaticText(self, wx.ID_ANY, "", size=(200, -1))
		hsz.Add(self.stFile, 0, wx.TOP, 4)
		
		hsz.AddSpacer(20)
		
		vsizer.Add(hsz)
		vsizer.AddSpacer(20)
		
		hsz = wx.BoxSizer(wx.HORIZONTAL)
		hsz.AddSpacer(10)
		
		self.bGo = wx.Button(self, wx.ID_ANY, "Audit")
		hsz.Add(self.bGo)
		self.Bind(wx.EVT_BUTTON, self.onbGo, self.bGo)
		
		hsz.AddSpacer(20)
		
		self.bExit = wx.Button(self, wx.ID_ANY, "Exit")
		hsz.Add(self.bExit)
		self.Bind(wx.EVT_BUTTON, self.onExit, self.bExit)
		
		hsz.AddSpacer(10)		
		vsizer.Add(hsz)
		vsizer.AddSpacer(20)
		
		sizer = wx.BoxSizer(wx.HORIZONTAL)
		sizer.AddSpacer(20)
		sizer.Add(vsizer)
		sizer.AddSpacer(20)
		
		self.checkGoEnable()
		
		self.SetSizer(sizer)
		self.Fit()
		
	def checkGoEnable(self):
		if self.currentCategory is None or self.currentFile is None:
			self.bGo.Enable(False)
		else:
			self.bGo.Enable(True)
		
	def onbFile(self, _):
		dlg = wx.FileDialog(self, message="Choose an ini file",
			defaultDir=self.root,
			defaultFile="",
			wildcard="INI File (*.ini)|*.ini",
			style=wx.FD_OPEN | wx.FD_FILE_MUST_EXIST)
		rc = dlg.ShowModal()
		if rc == wx.ID_OK:
			self.currentFile = dlg.GetPath()
			
		dlg.Destroy()
		if rc != wx.ID_OK:
			return 

		bn = os.path.basename(self.currentFile)
		self.stFile.SetLabel(bn)
		
		self.checkGoEnable()

	def onCategory(self, _):
		cx = self.chCategory.GetCurrentSelection()
		if cx != wx.NOT_FOUND:
			self.currentCategory = self.cats[cx]
		else:
			self.currentCategory = None
			
		self.checkGoEnable()
			
	def onbGo(self, _):
		parser = RawConfigParser()
		with open(self.currentFile) as stream:
			parser.read_string("[top]\n" + stream.read())

		fileKeys = []				
		for k, _ in parser.items("top"):
			fileKeys.append(k)
			
		fileKeys = sorted(fileKeys)
		jsonAttr = self.attrMap.getCatAttrs(self.currentCategory)
		jsonKeys = sorted([x["name"] for x in jsonAttr if "name" in x])
		
		new = []
		missing = []
		common = []
		
		for a in jsonKeys:
			if a not in fileKeys:
				missing.append(a)
			else:
				common.append(a)
				
		for a in fileKeys:
			if a not in jsonKeys:
				new.append(a)
				print("{\"name\": \"%s\", \"label\": \"%s\", \"type\": \"hidden\"}," % (a, a.replace("_", " ")))
						
		dlg = AuditReport(self, self.currentCategory, os.path.basename(self.currentFile), new, missing, common)
		dlg.ShowModal()
		dlg.Destroy()

	def onExit(self, _):
		self.EndModal(wx.ID_OK)
