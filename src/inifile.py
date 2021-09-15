import wx
import re

class IniFileDlg(wx.Dialog):
	def __init__(self, parent, cat, flist):
		wx.Dialog.__init__(self, parent, wx.ID_ANY, "")
		self.parent = parent
		self.category = cat
		self.flist = [x for x in flist]
				
		
		vsizer = wx.BoxSizer(wx.VERTICAL)
		vsizer.AddSpacer(20)
		
		st = wx.StaticText(self, wx.ID_ANY, "Save %s as:" % cat)
		vsizer.Add(st)
		vsizer.AddSpacer(10)
		
		self.cbFiles = wx.ComboBox(self, wx.ID_ANY, value="", choices=flist)
		vsizer.Add(self.cbFiles)
		
		vsizer.AddSpacer(10)
		
		hsz = wx.BoxSizer(wx.HORIZONTAL)
		hsz.AddSpacer(10)
		
		self.bOK = wx.Button(self, wx.ID_ANY, "OK")
		hsz.Add(self.bOK)
		self.Bind(wx.EVT_BUTTON, self.onbOK, self.bOK)
		hsz.AddSpacer(10)
		
		self.bCancel = wx.Button(self, wx.ID_ANY, "Cancel")
		self.Bind(wx.EVT_BUTTON, self.onbCancel, self.bCancel)
		hsz.Add(self.bCancel)
		
		hsz.AddSpacer(10)
		
		vsizer.Add(hsz)
		vsizer.AddSpacer(20)
		
		sizer = wx.BoxSizer(wx.HORIZONTAL)
		sizer.AddSpacer(20)
		sizer.Add(vsizer)
		sizer.AddSpacer(20)
		
		self.SetSizer(sizer)
		self.Fit()
		
	def onbOK(self, _):
		if self.cbFiles.IsTextEmpty():
			self.EndModal(wx.ID_CANCEL)
			return
			
		nfn = self.cbFiles.GetValue()
			
		if re.findall(r'[^A-Za-z0-9_\-\. ]', nfn):
			dlg = wx.MessageDialog(self,
				"Only alpha-numeric, dashes, underscores, or spaces allowed",
				"Invalid File Name",
				wx.OK | wx.ICON_WARNING)
			rc = dlg.ShowModal()
			dlg.Destroy()
			return
		
		nfnl = nfn.lower()
		flist = [x.lower() for x in self.flist]
		if nfnl in flist:
			dlg = wx.MessageDialog(self,
				"%s %s already exists.  Over-write?" % (self.category, nfn),
				"Over-write warning",
				wx.YES_NO | wx.NO_DEFAULT | wx.ICON_WARNING)
			rc = dlg.ShowModal()
			dlg.Destroy()
			if rc != wx.ID_YES:
				return
			
		self.EndModal(wx.ID_OK)
		
	def onbCancel(self, _):
		self.EndModal(wx.ID_CANCEL)
		
	def getChoice(self):
		if self.cbFiles.IsTextEmpty():
			return None
						
		return self.cbFiles.GetValue()
