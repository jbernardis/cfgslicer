import wx
import os
from zipfile import ZipFile, is_zipfile

class BundleDlg(wx.Dialog):
	def __init__(self, parent, root, dirs):
		wx.Dialog.__init__(self, parent, wx.ID_ANY, "Bundle Config files")
		self.parent = parent
		self.root = root
		self.dirs = dirs

		self.Bind(wx.EVT_CLOSE, self.onClose)
		
		vsizer = wx.BoxSizer(wx.VERTICAL)
		vsizer.AddSpacer(20)
		
		hsz = wx.BoxSizer(wx.HORIZONTAL)
		hsz.AddSpacer(20)
		
		hsz.Add(wx.StaticText(self, wx.ID_ANY, "Root:", size=(100, -1)), 0, wx.TOP, 4)
		hsz.AddSpacer(10)
		self.bRoot = wx.Button(self, wx.ID_ANY, "...", size=(20, -1))
		self.Bind(wx.EVT_BUTTON, self.onbRoot, self.bRoot)	
		hsz.Add(self.bRoot)		
		hsz.AddSpacer(10)
		self.stRoot = wx.StaticText(self, wx.ID_ANY, self.root, size=(400, -1))
		hsz.Add(self.stRoot, 0, wx.TOP, 4)		
		hsz.AddSpacer(20)
		vsizer.Add(hsz)
		vsizer.AddSpacer(20)
		
		hsz = wx.BoxSizer(wx.HORIZONTAL)
		hsz.AddSpacer(20)
		
		hsz.Add(wx.StaticText(self, wx.ID_ANY, "Bundle File:", size=(100, -1)), 0, wx.TOP, 4)
		hsz.AddSpacer(10)
		self.bZipFile = wx.Button(self, wx.ID_ANY, "...", size=(20, -1))
		self.Bind(wx.EVT_BUTTON, self.onbZipFile, self.bZipFile)	
		hsz.Add(self.bZipFile)		
		hsz.AddSpacer(10)
		self.stZipFile = wx.StaticText(self, wx.ID_ANY, "", size=(400, -1))
		self.zipfile = None
		hsz.Add(self.stZipFile, 0, wx.TOP, 4)		
		hsz.AddSpacer(20)
		vsizer.Add(hsz)
		vsizer.AddSpacer(20)
		
		
		hsz = wx.BoxSizer(wx.HORIZONTAL)
		hsz.AddSpacer(20)
		
		hsz.Add(wx.StaticText(self, wx.ID_ANY, "", size=(100, -1)), 0, wx.TOP, 4)
		hsz.AddSpacer(10)
		self.bGo = wx.Button(self, wx.ID_ANY, "GO")
		self.Bind(wx.EVT_BUTTON, self.onbGo, self.bGo)	
		self.bGo.Enable(False)
		hsz.Add(self.bGo)		
		hsz.AddSpacer(20)
		vsizer.Add(hsz)
		vsizer.AddSpacer(20)
		
		
		sizer = wx.BoxSizer(wx.HORIZONTAL)
		sizer.AddSpacer(20)
		sizer.Add(vsizer)
		sizer.AddSpacer(20)
		
		self.SetSizer(sizer)
		self.Fit()
		
	def onbRoot(self, _):
		dlg = wx.DirDialog(self, "Choose a directory:", style=wx.DD_DEFAULT_STYLE)		
		dlg.SetPath(self.root)
		rc = dlg.ShowModal()
		if rc == wx.ID_OK:
			self.root = dlg.GetPath()
			self.stRoot.SetLabel(self.root)

		dlg.Destroy()
		
	def onbZipFile(self, _):
		wildcard = "ZIP File (*.zip)|*.zip"
		dlg = wx.FileDialog(
			self, message="Save bundle as ...", defaultDir=os.getcwd(),
			defaultFile="", wildcard=wildcard, style=wx.FD_SAVE | wx.FD_OVERWRITE_PROMPT
			)
		rc = dlg.ShowModal()
		if rc == wx.ID_OK:
			self.zipfile = dlg.GetPath()
			self.stZipFile.SetLabel(self.zipfile)
			self.bGo.Enable(True)

		dlg.Destroy()

		
	def onbGo(self, _):
		cwd = os.getcwd()
		os.chdir(self.root)

		fl = []
		for d in self.dirs:
			fqdir = os.path.join(self.root, d)
			fl.extend([os.path.join(d, f) for f in os.listdir(fqdir) if os.path.isfile(os.path.join(fqdir, f)) and f.lower().endswith(".ini")])

		fc = 0			
		with ZipFile(self.zipfile, 'w') as zfp:
			for inifn in fl:
				zfp.write(inifn)
				fc += 1
				
		os.chdir(cwd)
		
		dlg = wx.MessageDialog(self, "%d files successfully written to\n%s" % (fc, self.zipfile), 'Bundle successfully written', wx.OK | wx.ICON_INFORMATION)
		dlg.ShowModal()
		dlg.Destroy()
		
	def onClose(self, _):
		self.EndModal(wx.ID_OK)

class UnBundleDlg(wx.Dialog):
	def __init__(self, parent, root, dirs):
		wx.Dialog.__init__(self, parent, wx.ID_ANY, "Un-Bundle Config ZIP file")
		self.parent = parent
		self.root = root
		self.dirs = dirs

		self.Bind(wx.EVT_CLOSE, self.onClose)
		
		vsizer = wx.BoxSizer(wx.VERTICAL)
		vsizer.AddSpacer(20)
		
		hsz = wx.BoxSizer(wx.HORIZONTAL)
		hsz.AddSpacer(20)	
		hsz = wx.BoxSizer(wx.HORIZONTAL)
		hsz.AddSpacer(20)
		
		hsz.Add(wx.StaticText(self, wx.ID_ANY, "Bundle File:", size=(100, -1)), 0, wx.TOP, 4)
		hsz.AddSpacer(10)
		self.bZipFile = wx.Button(self, wx.ID_ANY, "...", size=(20, -1))
		self.Bind(wx.EVT_BUTTON, self.onbZipFile, self.bZipFile)	
		hsz.Add(self.bZipFile)		
		hsz.AddSpacer(10)
		self.stZipFile = wx.StaticText(self, wx.ID_ANY, "", size=(400, -1))
		self.zipfile = None
		hsz.Add(self.stZipFile, 0, wx.TOP, 4)		
		hsz.AddSpacer(20)
		vsizer.Add(hsz)
		vsizer.AddSpacer(20)
		
		hsz = wx.BoxSizer(wx.HORIZONTAL)
		hsz.AddSpacer(20)
		
		hsz.Add(wx.StaticText(self, wx.ID_ANY, "Destination:", size=(100, -1)), 0, wx.TOP, 4)
		hsz.AddSpacer(10)
		self.bRoot = wx.Button(self, wx.ID_ANY, "...", size=(20, -1))
		self.Bind(wx.EVT_BUTTON, self.onbRoot, self.bRoot)	
		hsz.Add(self.bRoot)		
		hsz.AddSpacer(10)
		self.stRoot = wx.StaticText(self, wx.ID_ANY, self.root, size=(400, -1))
		hsz.Add(self.stRoot, 0, wx.TOP, 4)		
		hsz.AddSpacer(20)
		vsizer.Add(hsz)
		vsizer.AddSpacer(20)
		
		hsz = wx.BoxSizer(wx.HORIZONTAL)
		hsz.AddSpacer(20)
		
		hsz.Add(wx.StaticText(self, wx.ID_ANY, "", size=(100, -1)))
		hsz.AddSpacer(10)
		self.cbNewRoot = wx.CheckBox(self, wx.ID_ANY, "Set as root and reload")
		hsz.Add(self.cbNewRoot)		
		hsz.AddSpacer(20)
		vsizer.Add(hsz)
		vsizer.AddSpacer(20)
				
		hsz = wx.BoxSizer(wx.HORIZONTAL)
		hsz.AddSpacer(20)
		
		hsz.Add(wx.StaticText(self, wx.ID_ANY, "", size=(100, -1)), 0, wx.TOP, 4)
		hsz.AddSpacer(10)
		self.bGo = wx.Button(self, wx.ID_ANY, "GO")
		self.Bind(wx.EVT_BUTTON, self.onbGo, self.bGo)	
		self.bGo.Enable(False)
		hsz.Add(self.bGo)		
		hsz.AddSpacer(20)
		vsizer.Add(hsz)
		vsizer.AddSpacer(20)
		
				
		vsizer.Add(hsz)
		vsizer.AddSpacer(20)			
		
		self.SetSizer(vsizer)
		self.Fit()
		
	def onbZipFile(self, _):
		wildcard = "ZIP File (*.zip)|*.zip"
		dlg = wx.FileDialog(
			self, message="Save bundle as ...", defaultDir=os.getcwd(),
			defaultFile="", wildcard=wildcard, style=wx.FD_OPEN | wx.FD_FILE_MUST_EXIST
			)
		rc = dlg.ShowModal()
		if rc == wx.ID_OK:
			zf = dlg.GetPath()
			if not is_zipfile(zf):
				dlg.Destroy()
				self.bGo.Enable(False)
				dlg = wx.MessageDialog(self,
					"File %s is not a valid zip file" % zf,
					"Not a zip file",
					wx.OK | wx.ICON_ERROR)
				dlg.ShowModal()
				dlg.Destroy()
			else:
				self.zipfile = zf
				self.stZipFile.SetLabel(self.zipfile)
				self.bGo.Enable(True)
				dlg.Destroy()
		
	def onbRoot(self, _):
		dlg = wx.DirDialog(self, "Choose a directory:", style=wx.DD_DEFAULT_STYLE)		
		dlg.SetPath(self.root)
		rc = dlg.ShowModal()
		if rc == wx.ID_OK:
			self.root = dlg.GetPath()
			self.stRoot.SetLabel(self.root)

		dlg.Destroy()
		
	def onbGo(self, _):
		cwd = os.getcwd()
		os.chdir(self.root)

		with ZipFile(self.zipfile, 'r') as zfp:
			zfp.extractall()
				
		os.chdir(cwd)
		
		dlg = wx.MessageDialog(self, "successfully extracted\n%s\n  to\n%s" % (self.zipfile, self.root), 'Bundle successfully extracted', wx.OK | wx.ICON_INFORMATION)
		dlg.ShowModal()
		dlg.Destroy()
		
	def getNewRoot(self):
		if self.cbNewRoot.GetValue():
			return self.root
		else:
			return None
	
	def onClose(self, _):
		self.EndModal(wx.ID_OK)
