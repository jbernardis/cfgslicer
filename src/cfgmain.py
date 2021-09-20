import wx
import wx.propgrid as wxpg

from settings import Settings
from cfgslicer import CfgSlicer
from inifile import IniFileDlg
from auditfile import AuditFileDlg
from singlechoiceproperty import  SingleChoiceProperty
from colorproperty import ColorProperty
from attributemap import AttributeMap, STRINGTYPE, LONGSTRINGTYPE, COLORTYPE, INFILLTYPE, SHELLINFILLTYPE, SUPPORTINFILLTYPE, IRONINGTYPE, SEAMPOSTYPE, LIMITSUSAGE, HIDDEN, BOOLEAN
from bundle import BundleDlg, UnBundleDlg

MENU_AUDIT = 101
MENU_RELOAD = 102
MENU_BUNDLE = 103
MENU_UNBUNDLE = 104

class CfgMain(wx.Frame):
	def __init__(self):
		wx.Frame.__init__(self, None, wx.ID_ANY, "Slicer x Configuration x Manager", size=(500, 500))
		self.SetBackgroundColour(wx.Colour(255, 255, 255))
		self.Bind(wx.EVT_CLOSE, self.onClose)
		
		self.CenterOnScreen()

		self.CreateStatusBar()
		#self.SetStatusText("This is the statusbar")
		
		self.attrMap = AttributeMap("attributes.json")
		self.settings = Settings() 
		self.cats = self.attrMap.getCategories()
		
		self.cfg = CfgSlicer(self.settings.root, self.cats)
		
		menuBar = wx.MenuBar()

		# 1st menu from left
		menuTools = wx.Menu()
		menuTools.Append(MENU_AUDIT, "Audit", "Compare a file with configured options")
		menuTools.Append(MENU_RELOAD, "Reload", "Reload INI files")
		menuTools.Append(MENU_BUNDLE, "Bundle", "Bundle INI files into a ZIP file")
		menuTools.Append(MENU_UNBUNDLE, "Unbundle", "Unbundle INI files from a ZIP file")

		menuBar.Append(menuTools, "Tools")
		self.SetMenuBar(menuBar)
		self.Bind(wx.EVT_MENU, self.onAudit, id=MENU_AUDIT)
		self.Bind(wx.EVT_MENU, self.onReload, id=MENU_RELOAD)
		self.Bind(wx.EVT_MENU, self.onBundle, id=MENU_BUNDLE)
		self.Bind(wx.EVT_MENU, self.onUnbundle, id=MENU_UNBUNDLE)
				
		self.nchecked = 0
		self.propertiesChanged = False
		self.selected = None
		
		self.titleString = "Slicer Configuration Manager"
		self.setTitle()

		whsz = wx.BoxSizer(wx.HORIZONTAL)
		whsz.AddSpacer(20)
				
		wvsz = wx.BoxSizer(wx.VERTICAL)
		wvsz.AddSpacer(20)

		hsz = wx.BoxSizer(wx.HORIZONTAL)

		hsz.AddSpacer(20)				
		st = wx.StaticText(self, wx.ID_ANY, "Category:")
		hsz.Add(st, 0, wx.TOP, 4)
		hsz.AddSpacer(10)
		self.chCategory = wx.Choice(self, wx.ID_ANY, choices = self.cats)
		self.chCategory.SetSelection(0)
		self.currentCategory = self.cats[0]
		self.Bind(wx.EVT_CHOICE, self.onCategory, self.chCategory)
		hsz.Add(self.chCategory)
		hsz.AddSpacer(20)
		
		wvsz.Add(hsz)
		
		wvsz.AddSpacer(20)
		
		hsz = wx.BoxSizer(wx.HORIZONTAL)
		hsz.AddSpacer(20)
		
		vsz = wx.BoxSizer(wx.VERTICAL)
		vsz.AddSpacer(10)
		
		st = wx.StaticText(self, wx.ID_ANY, "Files:")
		vsz.Add(st, 0, wx.TOP, 4)
		vsz.AddSpacer(10)
		
		self.bAll = wx.Button(self, wx.ID_ANY, "All")
		self.Bind(wx.EVT_BUTTON, self.onBAll, self.bAll)
		vsz.Add(self.bAll)
		vsz.AddSpacer(10)
		
		self.bNone = wx.Button(self, wx.ID_ANY, "None")
		self.Bind(wx.EVT_BUTTON, self.onBNone, self.bNone)
		vsz.Add(self.bNone)
		vsz.AddSpacer(30)
		
		self.bCopy = wx.Button(self, wx.ID_ANY, "Copy")
		self.Bind(wx.EVT_BUTTON, self.onBCopy, self.bCopy)
		vsz.Add(self.bCopy)
		self.bCopy.Enable(False)
		vsz.AddSpacer(10)
		
		self.bDel = wx.Button(self, wx.ID_ANY, "Delete")
		self.Bind(wx.EVT_BUTTON, self.onBDel, self.bDel)
		vsz.Add(self.bDel)
		self.bDel.Enable(False)
		vsz.AddSpacer(10)
		
		hsz.Add(vsz)
		hsz.AddSpacer(10)
				
		self.lbFiles = wx.CheckListBox(self, wx.ID_ANY, size=(250, 200), choices=[])
		self.Bind(wx.EVT_LISTBOX, self.onFile, self.lbFiles)
		self.Bind(wx.EVT_LISTBOX_DCLICK, self.onFileDClick, self.lbFiles)
		self.Bind(wx.EVT_CHECKLISTBOX, self.onFileCheck, self.lbFiles)
		hsz.Add(self.lbFiles)
		
		hsz.AddSpacer(20)
		
		wvsz.Add(hsz)
		
		wvsz.AddSpacer(10)
		
		hsz = wx.BoxSizer(wx.HORIZONTAL)
		hsz.AddSpacer(20)
		
		self.bSave = wx.Button(self, wx.ID_ANY, "Save")
		self.bSave.Bind(wx.EVT_BUTTON, self.onSave, self.bSave)
		self.bSave.Enable(False)
		hsz.Add(self.bSave)
		
		hsz.AddSpacer(10)
		
		self.bCancel = wx.Button(self, wx.ID_ANY, "Cancel")
		self.bCancel.Bind(wx.EVT_BUTTON, self.onCancel, self.bCancel)
		self.bCancel.Enable(False)
		hsz.Add(self.bCancel)
		
		hsz.AddSpacer(20)
		
		wvsz.Add(hsz)

		wvsz.AddSpacer(20)	
		
		whsz.Add(wvsz)
		whsz.AddSpacer(10)
		
		wvsz = wx.BoxSizer(wx.VERTICAL)
		
		
		self.pg = wxpg.PropertyGrid(self, id=wx.ID_ANY, size=(1000, 300))
		wvsz.Add(self.pg)
		self.pg.Bind(wxpg.EVT_PG_CHANGED, self.onPropertyChange)
		
		
		wvsz.AddSpacer(20)	
		whsz.Add(wvsz)
		
		whsz.AddSpacer(20)	
		
		vsz = wx.BoxSizer(wx.VERTICAL)
		vsz.AddSpacer(20)
		vsz.Add(whsz)
		vsz.AddSpacer(20)
		
		self.SetSizer(vsz)
		
		self.Layout()
		self.Fit()
		self.Show()
		
		self.loadCategory(self.currentCategory)
		p = int(self.pg.GetSplitterPosition()/2)
		if p < 250:
			p = 250
		self.pg.SetSplitterPosition(p)
		
	def setTitle(self):
		if self.propertiesChanged:
			self.SetTitle(self.titleString + "  *")
		else:
			self.SetTitle(self.titleString)
		
	def onCategory(self, _):
		cx = self.chCategory.GetCurrentSelection()
		if cx != wx.NOT_FOUND:
			self.currentCategory = self.cats[cx]
			self.loadCategory(self.currentCategory)

	def loadCategory(self, cat):
		self.fl = self.cfg.getFileList(cat)
		#self.fl = [os.path.splitext(x)[0] for x in fl]
		self.lbFiles.Set(self.fl)
		self.nchecked = 0
		self.allowDelete(False)
		self.allowCopy(False)
		idx = self.lbFiles.GetSelection()
		idxl = []
		if idx != wx.NOT_FOUND:
			idxl  = [ idx ]
		self.loadProperties(idxl)

	def onFile(self, evt):
		if self.nchecked == 0:	
			idx = evt.GetSelection()
			if idx != wx.NOT_FOUND:
				self.loadProperties([idx])
				self.selected = idx
				self.allowCopy()
				self.allowDelete()
			else:
				self.loadProperties([])
				self.selected = None
				self.allowCopy(False)
				self.allowDelete(False)

	def onFileCheck(self, evt):
		index = evt.GetSelection()
		if index == wx.NOT_FOUND:
			return
		
		self.lbFiles.SetSelection(index)
		if self.lbFiles.IsChecked(index):
			self.nchecked += 1
		else:
			self.nchecked -= 1
		
		if self.nchecked == 0:
			self.loadProperties([index])
			self.selected = index
			self.allowCopy()
			self.allowDelete()
		else:
			self.loadProperties(self.getCheckedList())
			self.selected = None
			self.allowCopy(False)
			self.allowDelete(False)
			
	def onFileDClick(self, evt):
		index = evt.GetSelection()
		if index == wx.NOT_FOUND:
			return
		
		self.lbFiles.SetSelection(index)
		if self.lbFiles.IsChecked(index):
			self.lbFiles.Check(index, False)
			self.nchecked -= 1
		else:
			self.lbFiles.Check(index, True)
			self.nchecked += 1
		
		if self.nchecked == 0:
			self.loadProperties([index])
			self.selected = index
			self.allowCopy()
			self.allowDelete()
		else:
			self.loadProperties(self.getCheckedList())
			self.selected = None
			self.allowCopy(False)
			self.allowDelete(False)
		
	def onBAll(self, _):
		for i in range(len(self.fl)):
			self.lbFiles.Check(i, True)
		self.nchecked = len(self.fl)
		self.loadProperties(self.getCheckedList())
		self.selected = None
		self.allowCopy(False)
		self.allowDelete(False)
		
	def onBNone(self, _):
		for i in range(len(self.fl)):
			self.lbFiles.Check(i, False)
			
		self.nchecked = 0
		index = self.lbFiles.GetSelection()
		
		if index == wx.NOT_FOUND:
			self.selected = None
			self.allowCopy(False)
			self.allowDelete(False)
			self.loadProperties([])
		else:
			self.selected = index
			self.allowCopy(True)
			self.allowDelete(True)
			self.loadProperties([index])
			
	def allowCopy(self, flag=True):
		if self.propertiesChanged:
			self.bCopy.Enable(False)
		self.bCopy.Enable(flag)
			
	def allowDelete(self, flag=True):
		if len(self.fl) <= 1 or self.propertiesChanged:
			self.bDel.Enable(False)
		else:
			self.bDel.Enable(flag)
			
	def onBCopy(self, _):
		cat = self.currentCategory
		fl = self.cfg.getFileList(cat)
		
		dlg = IniFileDlg(self, cat, fl)
		rc = dlg.ShowModal()
		if rc == wx.ID_OK:
			path = dlg.getChoice()

		dlg.Destroy()
		
		if rc != wx.ID_OK:
			return

		fn = self.lbFiles.GetString(self.selected)
		self.cfg.copyFile(cat, fn, path, force=True)
		self.loadCategory(cat)
		fl = self.cfg.getFileList(cat)
		idx = fl.index(path)

		self.lbFiles.SetSelection(idx)
		self.selected = idx
		self.allowDelete()
		self.allowCopy()
		self.loadProperties([idx])
		
	def onBDel(self, _):
		fn = self.lbFiles.GetString(self.selected)
		dlg = wx.MessageDialog(self,
			"Delete %s %s?" % (self.currentCategory, fn),
			"Delete File",
			wx.YES_NO | wx.NO_DEFAULT | wx.ICON_WARNING)
		rc = dlg.ShowModal()
		dlg.Destroy()
		if rc != wx.ID_YES:
			return
		
		self.cfg.deleteFile(self.currentCategory, fn)

		self.loadCategory(self.currentCategory)		
		fl = self.cfg.getFileList(self.currentCategory)
		idx = self.selected
		if idx >= len(fl):
			idx = len(fl)-1
			
		if idx < 0:
			self.selected = None
			self.lbFiles.SetSelection(wx.NOT_FOUND)
			self.loadProperties([])
			self.allowCopy(False)
			self.allowDelete(False)
			
		else:
			self.selected = idx
			self.lbFiles.SetSelection(idx)
			self.loadProperties([idx])
			self.allowCopy(True)
			self.allowDelete(len(fl) != 1)
		
	def getCheckedList(self):
		cl = []
		for i in range(len(self.fl)):
			if self.lbFiles.IsChecked(i):
				cl.append(i)
				
		return cl
	
	def loadProperties(self, idxl):
		self.pg.Clear()
		cat = self.currentCategory
		self.acl = {}
		
		if len(idxl) == 0:
			return
		
		for fx in idxl:
			fn = self.lbFiles.GetString(fx)
			al = self.cfg.getAttributes(cat, fn)
			for label in al:
				a = self.attrMap.getSingleAttribute(cat, label)
				if a and a["type"] == BOOLEAN:
					value = 'False' if al[label] == '0' else 'True'
				else:
					value = al[label]
				if label not in self.acl:
					self.acl[label] = []
					
				if value not in self.acl[label]:
					self.acl[label].append(value)
					
		if len(self.acl) == 0:
			return
					
		clist = self.attrMap.getGroups(cat)
		for c in clist:
			self.pg.Append( wxpg.PropertyCategory(c+":") )	
			grpAttrs = self.attrMap.getGroupAttrs(cat, c)
			for attr in grpAttrs:
				name = attr["name"]
				label = attr["label"]
				atype = attr["type"]
									
				try:
					al = self.acl[name]
				except KeyError:
					print("Attribute (%s) missing" % name)
					al = [""]

				if atype != HIDDEN:					
					if len(al) > 1:
						al = ["<keep>"] + al
						al = [[x, x] for x in al]
						self.pg.Append(SingleChoiceProperty(label, name, al[0][1], al, "%s (%s)" % (label, name), "Choose value to use"))
					else:
						if atype == COLORTYPE:
							p = ColorProperty(label, name, value=al[0])
							self.pg.Append(p)
							self.pg.LimitPropertyEditing(p, True)
							
						elif atype in [ INFILLTYPE, SHELLINFILLTYPE, SUPPORTINFILLTYPE, IRONINGTYPE, SEAMPOSTYPE, LIMITSUSAGE ]:
							l = self.attrMap.getChoices(atype)
							p = SingleChoiceProperty(label, name, al[0], l, "%s (%s)" % (label, name), "Choose value to use")
							self.pg.Append(p)
							self.pg.LimitPropertyEditing(p, True)
							
						elif atype == STRINGTYPE:
							self.pg.Append(wxpg.StringProperty(label, name, value=al[0]) )
						
						elif atype == LONGSTRINGTYPE:
							p = wxpg.LongStringProperty(label, name, value=al[0])
							self.pg.Append(p)
							self.pg.LimitPropertyEditing(p, True)
						
						elif atype == BOOLEAN:
							p = wxpg.BoolProperty(label, name, value=(al[0] != 'False'))
							self.pg.Append(p)
							self.pg.LimitPropertyEditing(p, True)
														
						else:
							print("invalid type for field %s: %s" % (name, atype))

	def onPropertyChange(self, evt):
		self.enablePendingChanges(True)
		
	def enablePendingChanges(self, flag=True):
		self.propertiesChanged = flag
		self.bSave.Enable(flag)
		self.bCancel.Enable(flag)
		if flag:
			self.allowCopy(False)
			self.allowDelete(False)
			self.SetStatusText("Changes pending")
		else:
			if self.nchecked == 0:	
				self.allowCopy(True)
				self.allowDelete(True)
			else:
				self.allowCopy(False)
				self.allowDelete(False)
			self.SetStatusText("")
			
		self.lbFiles.Enable(not flag)
		self.chCategory.Enable(not flag)
		self.setTitle()
		
	def onSave(self, _):
		it = self.pg.GetIterator()
		pgl = {}
		while not it.AtEnd():
			p = it.GetProperty()
			pgl[p.GetName()] =  p.GetValue()
			it.Next()
			
		cat = self.currentCategory
		if self.nchecked == 0:
			idxl = [ self.lbFiles.GetSelection() ]
		else:
			idxl = self.getCheckedList()
			
		for fx in idxl:
			fn = self.lbFiles.GetString(fx)

			clist = self.attrMap.getGroups(cat)
			for c in clist:
				grpAttrs = self.attrMap.getGroupAttrs(cat, c)
				for attr in grpAttrs:
					name = attr["name"]
					if attr["type"] != HIDDEN:
						try:
							oldv = self.cfg.getAttribute(cat, fn, name)
						except:
							oldv = None
						if attr["type"] == BOOLEAN:
							if pgl[name] == 'True':
								print("string true for %s" % name)
								newv = True
							elif pgl[name] == 'False':
								print("string false for %s" % name)
								newv = False
							else:
								print("true boolean value for %s" % name)
								newv = '1' if pgl[name] else '0'
						else:
							newv = pgl[name]

						print("%s: oldval (%s) newval(%s)" % (name, oldv, newv))
						if oldv is None or (newv != "<keep>" and newv != oldv):
							self.cfg.setAttribute(cat, fn, name, newv)
							print("updated attributes")
					else:
						print("hidden attribute: %s" % name)
	
		self.cfg.writeModified()				
		self.enablePendingChanges(False)
		
	def onCancel(self, _):
		if not self.verifyLoseChanges("cancel"):
			return 
		
		self.enablePendingChanges(False)
		if self.nchecked == 0:
			idxl = [ self.lbFiles.GetSelection() ]
		else:
			idxl = self.getCheckedList()
			
		self.loadProperties(idxl)
		
	def onAudit(self, _):
		dlg = AuditFileDlg(self, self.settings.root, self.attrMap, self.cats)
		dlg.ShowModal()
		dlg.Destroy()
		
	def onReload(self, _):
		if self.propertiesChanged:
			if not self.verifyLoseChanges("reload"):
				return 

		self.cfg = CfgSlicer(self.settings.root, self.cats)
		self.selected = None
		self.lbFiles.SetSelection(wx.NOT_FOUND)
		self.loadProperties([])
		self.enablePendingChanges(False)
		self.allowCopy(False)
		self.allowDelete(False)
		
	def onBundle(self, _):
		dlg = BundleDlg(self, self.settings.root, self.cats)
		dlg.ShowModal()
		dlg.Destroy()
		
	def onUnbundle(self, _):
		dlg = UnBundleDlg(self, self.settings.root)
		dlg.ShowModal()
		dlg.Destroy()
				
	def onClose(self, _):
		if self.propertiesChanged:
			if not self.verifyLoseChanges("exit"):
				return 
			
		self.Destroy()
		
	def verifyLoseChanges(self, action):
		dlg = wx.MessageDialog(self,
							"You have not written your pending changes.\nAre you sure you want to %s?" % action,
							"Unwritten Changes",
							wx.YES_NO | wx.NO_DEFAULT | wx.ICON_WARNING)
		rc = dlg.ShowModal()
		dlg.Destroy()

		return rc == wx.ID_YES


if __name__ == '__main__':
	app = wx.App()
	frame = CfgMain()
	frame.Show(True)
	app.MainLoop()