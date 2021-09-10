import json
import wx
import wx.propgrid as wxpg

from settings import Settings
from cfgslicer import CfgSlicer
from inifile import IniFileDlg
from cfgexceptions import CfgInvalidColor

STRINGTYPE = "string"
COLORTYPE = "color"

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

class SingleChoiceDialogAdapter(wxpg.PGEditorDialogAdapter):
	def __init__(self, choices, message, caption):
		wxpg.PGEditorDialogAdapter.__init__(self)
		self.choices = choices
		self.message = message
		self.caption = caption

	def DoShowDialog(self, propGrid, _):
		s = wx.GetSingleChoice(self.message, self.caption, self.choices)
		
		if s:
			self.SetValue(s)
			return True
		
		return False;
	
class SingleChoiceProperty(wxpg.StringProperty):
	def __init__(self, label, name, value, choices, message, caption):
		wxpg.StringProperty.__init__(self, label, name, value)
		
		self.dialog_choices = [x for x in choices]
		self.message = message
		self.caption = caption

	def DoGetEditorClass(self):
		return wxpg.PropertyGridInterface.GetEditorByName("TextCtrlAndButton")

	def GetEditorDialog(self):
		return SingleChoiceDialogAdapter(self.dialog_choices, self.message, self.caption)
	
class ColorDialogAdapter(wxpg.PGEditorDialogAdapter):
	def __init__(self, prop):
		wxpg.PGEditorDialogAdapter.__init__(self)
		self.prop = prop

	def DoShowDialog(self, propGrid, _):
		cval = self.prop.GetValue()
		try:
			r, g, b = parseColorValue(cval)
		except CfgInvalidColor:
			r = 0
			g = 0
			b = 0
			
		dlg = wx.ColourDialog(None)
		dlg.GetColourData().SetChooseFull(True)
		dlg.GetColourData().SetColour(wx.Colour(r, g, b, wx.ALPHA_OPAQUE))

		rc = dlg.ShowModal()
		if rc == wx.ID_OK:
			data = dlg.GetColourData()
			color = data.GetColour()
			r = color.Red()
			g = color.Green()
			b = color.Blue()

		dlg.Destroy()
		
		if rc != wx.ID_OK:
			return False
		
		cval = "#%02X%02X%02X" % (r, g, b)
		self.SetValue(cval)
		return True

class ColorProperty(wxpg.StringProperty):
	def __init__(self, label, name, value):
		wxpg.StringProperty.__init__(self, label, name, value)

	def DoGetEditorClass(self):
		return wxpg.PropertyGridInterface.GetEditorByName("TextCtrlAndButton")

	def GetEditorDialog(self):
		return ColorDialogAdapter(self)

class CfgMain(wx.Frame):
	def __init__(self):
		wx.Frame.__init__(self, None, wx.ID_ANY, "Slicer x Configuration x Manager", size=(500, 500))
		self.SetBackgroundColour(wx.Colour(255, 255, 255))
		self.Bind(wx.EVT_CLOSE, self.onClose)
		
		with open("attributes.json", "r") as fp:
			self.attrMap = json.load(fp)
		self.settings = Settings() 
		self.cats = list(self.attrMap.keys())
		
		self.cfg = CfgSlicer(self.settings.root, self.cats)
		
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
		self.SetSizer(whsz)
		
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
		self.loadProperties(self.getCheckedList())

	def onFile(self, evt):
		if self.nchecked == 0:	
			index = evt.GetSelection()
			self.loadProperties([index])
			self.selected = index
			self.allowCopy()
			self.allowDelete()

	def onFileCheck(self, evt):
		index = evt.GetSelection()
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
		self.loadProperties([])

		index = self.lbFiles.GetSelection()
		if index == wx.NOT_FOUND:
			self.selected = None
			self.allowCopy(False)
			self.allowDelete(False)
		else:
			self.selected = index
			self.allowCopy(True)
			self.allowDelete(True)
			
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

		
		for fx in idxl:
			fn = self.lbFiles.GetString(fx)
			al = self.cfg.getAttributes(cat, fn)
			for label in al:
				value = al[label]
				if label not in self.acl:
					self.acl[label] = []
					
				if value not in self.acl[label]:
					self.acl[label].append(value)
					
		if len(self.acl) == 0:
			return
					
		clist = self.attrMap[cat]["categories"]
		for c in clist:
			self.pg.Append( wxpg.PropertyCategory(c+":") )	
			for attr in self.attrMap[cat][c]:
				name = attr["name"]
				try:
					label = attr["label"]
				except:
					label = name
					
				try:
					atype = attr["type"]
				except KeyError:
					atype = STRINGTYPE
									
				try:
					al = self.acl[name]
				except KeyError:
					print("Attribute (%s) missing" % name)
					al = [""]
					
				if len(al) > 1:
					al = ["<keep>"] + al
					self.pg.Append(SingleChoiceProperty(label, name, al[0], al, "%s (%s)" % (label, name), "Choose value to use"))
				else:
					if atype == COLORTYPE:
						self.pg.Append(ColorProperty(label, name, value=al[0]) )
					else:
						self.pg.Append(wxpg.StringProperty(label, name, value=al[0]) )
		
	def onPropertyChange(self, evt):
		self.enablePendingChanges(True)
		
	def enablePendingChanges(self, flag=True):
		self.propertiesChanged = flag
		self.bSave.Enable(flag)
		self.bCancel.Enable(flag)
		if flag:
			self.allowCopy(False)
			self.allowDelete(False)
		elif self.nchecked == 0:	
			self.allowCopy(True)
			self.allowDelete(True)
			
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
			
			clist = self.attrMap[cat]["categories"]
			for c in clist:
				
				
				for attr in self.attrMap[cat][c]:
					name = attr["name"]
					try:
						ov = self.cfg.getAttribute(cat, fn, name)
					except:
						ov = None
						
					if ov is None or (pgl[name] != "<keep>" and pgl[name] != ov):
						self.cfg.setAttribute(cat, fn, name, pgl[name])
	
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