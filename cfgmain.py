import wx
import wx.propgrid as wxpg
import os
import inspect
import logging
import json

logfile = "cfgslicer.log"
loglevel = logging.DEBUG

cmdFolder = os.path.realpath(os.path.abspath(os.path.split(inspect.getfile(inspect.currentframe()))[0]))

from settings import Settings
from cfgslicer import CfgSlicer
from filterdlg import FilterDlg
from inifile import IniFileDlg
from auditfile import AuditFileDlg
from singlechoiceproperty import SingleChoiceProperty, ChoiceToValue
from attributemap import AttributeMap, STRINGTYPE, LONGSTRINGTYPE, COLORTYPE, HIDDEN, BOOLEAN
from bundle import BundleDlg, UnBundleDlg
from cfgexceptions import CfgUnknownAttribute, CfgUnknownCategory, CfgUnknownFile

MENU_TOOLS = 100
MENU_TOOLS_AUDIT = 101
MENU_TOOLS_RELOAD = 102
MENU_TOOLS_BUNDLE = 103
MENU_TOOLS_UNBUNDLE = 104

MENU_SETTINGS = 200
MENU_SETTINGS_ROOT = 201
MENU_SETTINGS_ATTRIB = 202
MENU_SETTINGS_VERSION = 203


class CfgMain(wx.Frame):
	def __init__(self):
		wx.Frame.__init__(self, None, wx.ID_ANY, "Slicer x Configuration x Manager", size=(500, 500))
		self.Bind(wx.EVT_CLOSE, self.onClose)
		self.SetBackgroundColour(wx.Colour(255, 255, 255))
		
		self.CenterOnScreen()

		self.CreateStatusBar()
		
		menuBar = wx.MenuBar()

		menuSettings = wx.Menu()
		menuSettings.Append(MENU_SETTINGS_ROOT, "Slicer Configuration Root", "set new location for slicer configuration files")
		menuSettings.Append(MENU_SETTINGS_ATTRIB, "Attribute map", "set new location for slicer attributes map")
		menuSettings.Append(MENU_SETTINGS_VERSION, "Update version", "set new attribute map version to that of the slicer")
		menuBar.Append(menuSettings, "Settings")
		
		menuTools = wx.Menu()
		menuTools.Append(MENU_TOOLS_AUDIT, "Audit", "Compare a slicer configuration file against current attribute map")
		menuTools.Append(MENU_TOOLS_RELOAD, "Reload", "Reload slicer configuration files")
		menuTools.AppendSeparator()
		menuTools.Append(MENU_TOOLS_BUNDLE, "Bundle", "Bundle slicer configuration files into a ZIP file")
		menuTools.Append(MENU_TOOLS_UNBUNDLE, "Unbundle", "Extract slicer configuration files from a ZIP file")
		menuBar.Append(menuTools, "Tools")
		
		self.SetMenuBar(menuBar)

		logging.basicConfig(filename=logfile,
				filemode='w',
				format='%(asctime)s - %(levelname)s - %(message)s',
				level=loglevel)	

		sz = wx.BoxSizer()		
		self.panel = CfgPanel(self)
		sz.Add(self.panel)
		self.SetSizer(sz)
		
		self.Layout()
		self.Fit()
		self.Show()
		
		self.Bind(wx.EVT_MENU, self.panel.onAudit, id=MENU_TOOLS_AUDIT)
		self.Bind(wx.EVT_MENU, self.panel.onReload, id=MENU_TOOLS_RELOAD)
		self.Bind(wx.EVT_MENU, self.panel.onBundle, id=MENU_TOOLS_BUNDLE)
		self.Bind(wx.EVT_MENU, self.panel.onUnbundle, id=MENU_TOOLS_UNBUNDLE)
		self.Bind(wx.EVT_MENU, self.panel.onRoot, id=MENU_SETTINGS_ROOT)
		self.Bind(wx.EVT_MENU, self.panel.onAttrib, id=MENU_SETTINGS_ATTRIB)
		self.Bind(wx.EVT_MENU, self.panel.onVersion, id=MENU_SETTINGS_VERSION)

	def onClose(self, _):
		if not self.panel.okToClose():
			return
			
		self.Destroy()


class CfgPanel(wx.Panel):
	def __init__(self, parent):
		wx.Panel.__init__(self, parent, wx.ID_ANY, style=wx.TAB_TRAVERSAL)
		self.parent = parent

		self.settings = Settings(cmdFolder) 
		self.attrMap = AttributeMap(self.settings.attrFile)
		self.cats = self.attrMap.getCategories()
		self.choiceTypes = self.attrMap.getChoiceTypes()
		self.fl = None
		self.acl = {}
		self.extGroups = []

		self.cfg = CfgSlicer(self.settings.root, self.cats, self.attrMap)
		md = self.cfg.getMissingDirs()
		if len(md) > 0:
			self.parent.SetStatusText("Configuration directories missing: %s" % str(md))
			self.badConfig = True
		else:
			self.badConfig = False

		self.extGroup = self.attrMap.getExtruderGroup()
				
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
		self.chCategory = wx.Choice(self, wx.ID_ANY, choices=self.cats)
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
		vsz.AddSpacer(10)

		self.bFilter = wx.Button(self, wx.ID_ANY, "Filter")
		self.Bind(wx.EVT_BUTTON, self.onBFilter, self.bFilter)
		vsz.Add(self.bFilter)
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
		self.pg.SetExtraStyle(wx.propgrid.PG_EX_HELP_AS_TOOLTIPS)
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
		
		self.loadCategory(self.currentCategory)
		wx.CallAfter(self.checkVersions)

	def checkVersions(self):
		sversion = self.cfg.getSlicerVersion()
		aversion = self.attrMap.getAttributeVersion()
		if aversion != sversion:
			msg = "Slicer version %s\n does not match attribute version %s" % (sversion, aversion)
			dlg = wx.MessageDialog(self, msg, "Version mismatch", wx.OK | wx.ICON_WARNING)
			dlg.ShowModal()
			dlg.Destroy()

	def setTitle(self):
		ts = self.titleString + " - " + self.settings.root
		if self.propertiesChanged:
			ts += "  *"
			
		self.parent.SetTitle(ts)
		
	def onCategory(self, _):
		cx = self.chCategory.GetCurrentSelection()
		if cx != wx.NOT_FOUND:
			self.currentCategory = self.cats[cx]
			self.loadCategory(self.currentCategory)

	def loadCategory(self, cat):
		if self.badConfig:
			logging.error("returning from loadcategory due to bad configuration")
			self.fl = []
			return 
		
		self.fl = self.cfg.getFileList(cat)
		self.lbFiles.Set(self.fl)
		self.nchecked = 0
		self.allowDelete(False)
		self.allowCopy(False)
		idx = self.lbFiles.GetSelection()
		idxl = []
		if idx != wx.NOT_FOUND:
			idxl  = [idx]
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

	def onBFilter(self, _):
		dlg = FilterDlg(self, self.fl, self.attrMap, self.cfg, self.currentCategory)
		rc = dlg.ShowModal()
		fxl = []
		if rc == wx.ID_OK:
			fxl = dlg.getResults()
		dlg.Destroy()
		if rc != wx.ID_OK:
			return

		# first uncheck everythiong
		for i in range(len(self.fl)):
			self.lbFiles.Check(i, False)

		# now check the ones the dialog box returned
		for fx in fxl:
			self.lbFiles.Check(fx, True)

		self.nchecked = len(fxl)
		self.loadProperties(self.getCheckedList())
		self.selected = None
		self.allowCopy(False)
		self.allowDelete(False)

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
		path = None
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
		if self.badConfig:
			logging.error("returning from loadproperties due to bad configuration")
			return
		
		self.pg.Clear()
		cat = self.currentCategory
		self.acl = {}
		self.extGroups = []
		
		if len(idxl) == 0:
			return

		nExt = None		
		for fx in idxl:
			fn = self.lbFiles.GetString(fx)
			al = self.cfg.getAttributes(cat, fn)
			nx = self.cfg.getExtruderCount(fn)
			if nx is not None:
				nExt = nx
				
			for label in al:
				a = self.attrMap.getSingleAttribute(cat, label)
				if a:
					if self.attrMap.isExtruderAttribute(cat, label):
						logging.debug("%s is an extruder attribute" % label)
						vl = al[label].split(",")
						if len(vl) < nExt:
							vl.extend([vl[0]] * (nExt-len(vl)))
						elif len(vl) > nExt:
							vl = vl[:nExt]
						vl = [self.parseAttribute(v, a["type"]) for v in vl]
						value = vl
					else:
						value = self.parseAttribute(al[label], a["type"])
					logging.debug("attribute %s value: (%s)" % (label, str(value)))
				else:
					# no attribute found!!
					value = al[label]
					logging.warning("no attributes found for (%s:%s)" % (cat, label))
				if label not in self.acl:
					self.acl[label] = []
					
				if value not in self.acl[label]:
					self.acl[label].append(value)
					
		p = int(self.pg.GetSplitterPosition()/2)
		if p < 250:
			p = 250
		self.pg.SetSplitterPosition(p)

		if len(self.acl) == 0:
			return
					
		clist = self.attrMap.getGroups(cat)
		for c in clist:
			if self.attrMap.isExtruderGroup(cat, c):
				for ex in range(nExt):
					self.populateGroup(cat, c, ex+1)
			else:
				self.populateGroup(cat, c)
	
	@staticmethod
	def parseAttribute(v, t):
		if t == BOOLEAN:
			if v in ['0', "False", "false", "nil"]:
				return 'False'
			elif v in ['1', "True", "true"]:
				return 'True'
			else:
				logging.info("interpreting unknown value (%s) as True" % v)
				return 'True'
		else:  # not a boolean
			return v

	def populateGroup(self, cat, group, ext=None):
		if ext is None:
			lbl = group
			sfx = ""
		else:
			lbl = group % ext
			self.extGroups.append(lbl)
			sfx = "%d" % ext
			
		logging.debug("populate group (%s) (%s) (%s)" % (cat, group, lbl))
		self.pg.Append(wxpg.PropertyCategory(lbl+":"))
		baseColor = self.pg.GetBackgroundColour()
		currentColor = baseColor
		currentGroup = ""
		grpAttrs = self.attrMap.getGroupAttrs(cat, group)
		for attr in grpAttrs:
			if "subgroup" in attr:
				currentGroup = attr["subgroup"]
				if "color" in attr:
					currentColor = wx.Colour(attr["color"])
				else:
					currentColor = baseColor
				continue

			name = attr["name"]
			label = attr["label"]
			atype = attr["type"]
								
			try:
				al = self.acl[name]
			except KeyError:
				logging.debug("Attribute (%s) missing" % name)
				al = [""]

			if atype != HIDDEN:
				nm = name+sfx
				helpString = "%s/%s" % (currentGroup, nm)
				if len(al) > 1:
					al = ["<keep>"] + al
					al = [[x, x] for x in al]
					p = SingleChoiceProperty(label, nm, al[0][1], al, "%s (%s)" % (label, name), "Choose value to use")
					self.pg.Append(p)
					self.pg.SetPropertyBackgroundColour(p, currentColor)
					self.pg.SetPropertyHelpString(p, helpString)
				else:
					val = al[0]
					if ext is not None:
						val = val[ext-1]
						
					if atype == COLORTYPE:
						try:
							v1 = int(val[1:3], 16)
							v2 = int(val[3:5], 16)
							v3 = int(val[5:], 16)
							val = (v1, v2, v3, 255)
						except ValueError:
							val = (255, 255, 255, 255)

						p = wxpg.ColourProperty(label, nm, value=val)
						self.pg.Append(p)
						self.pg.SetPropertyBackgroundColour(p, currentColor)
						self.pg.SetPropertyHelpString(p, helpString)
						self.pg.LimitPropertyEditing(p, True)
						
					elif atype in self.choiceTypes:
						l = self.attrMap.getChoices(atype)
						p = SingleChoiceProperty(label, nm, val, l, "%s (%s)" % (label, name), "Choose value to use")
						self.pg.Append(p)
						self.pg.SetPropertyBackgroundColour(p, currentColor)
						self.pg.LimitPropertyEditing(p, True)
						self.pg.SetPropertyHelpString(p, helpString)

					elif atype == STRINGTYPE:
						p = wxpg.StringProperty(label, nm, value=val)
						self.pg.Append(p)
						self.pg.SetPropertyBackgroundColour(p, currentColor)
						self.pg.SetPropertyHelpString(p, helpString)

					elif atype == LONGSTRINGTYPE:
						p = wxpg.LongStringProperty(label, nm, value=val)
						self.pg.Append(p)
						self.pg.SetPropertyBackgroundColour(p, currentColor)
						self.pg.LimitPropertyEditing(p, True)
						self.pg.SetPropertyHelpString(p, helpString)

					elif atype == BOOLEAN:
						p = wxpg.BoolProperty(label, nm, value=(val != 'False'))
						self.pg.Append(p)
						self.pg.SetPropertyBackgroundColour(p, currentColor)
						self.pg.LimitPropertyEditing(p, True)
						self.pg.SetPropertyHelpString(p, helpString)

					else:
						logging.error("invalid type for field %s: %s" % (name, atype))

	def onPropertyChange(self, _):
		self.enablePendingChanges(True)

	def enablePendingChanges(self, flag=True):
		self.propertiesChanged = flag
		self.bSave.Enable(flag)
		self.bCancel.Enable(flag)
		if flag:
			self.allowCopy(False)
			self.allowDelete(False)
			self.parent.SetStatusText("Changes pending")
		else:
			if self.nchecked == 0:	
				self.allowCopy(True)
				self.allowDelete(True)
			else:
				self.allowCopy(False)
				self.allowDelete(False)
			self.parent.SetStatusText("")
			
		self.lbFiles.Enable(not flag)
		self.chCategory.Enable(not flag)
		self.setTitle()
		
	def onSave(self, _):
		it = self.pg.GetIterator()
		pgl = {}
		while not it.AtEnd():
			p = it.GetProperty()
			pgl[p.GetName()] = p.GetValue()
			it.Next()
			
		cat = self.currentCategory
		if self.nchecked == 0:
			idxl = [self.lbFiles.GetSelection()]
		else:
			idxl = self.getCheckedList()
	
		logging.debug("saving attributes")
		skipped = {}
		for fx in idxl:
			fn = self.lbFiles.GetString(fx)
			logging.debug("for file %s" % fn)

			clist = self.attrMap.getGroups(cat)
			logging.debug("groups: (%s)" % (str(clist)))
			fskipped = []
			for c in clist:
				if self.attrMap.isExtruderCategory(cat) and self.attrMap.isExtruderGroup(cat, c):
					logging.debug("extruder group: %s:%s" % (cat, c))
					extGrpCount = len(self.extGroups)
				else:
					extGrpCount = 0
					logging.debug("NOT extruder group: %s:%s" % (cat, c))
				grpAttrs = [a for a in self.attrMap.getGroupAttrs(cat, c) if "subgroup" not in a]
				for attr in grpAttrs:

					name = attr["name"]
					if attr["type"] != HIDDEN:
						skip = False
						logging.debug("attr name: *%s)" % name)
						try:
							oldv = self.cfg.getAttribute(cat, fn, name)
						except (CfgUnknownCategory, CfgUnknownFile):
							oldv = None
						except CfgUnknownAttribute:
							oldv = None
							skip = True
							
						if skip:
							fskipped.append("%s:%s" % (c, name))
						else:
							newv = self.getNewValue(name, attr, pgl, extGrpCount)
							if attr["type"] in self.choiceTypes:
								choices = self.attrMap.getChoices(attr["type"])
								v = ChoiceToValue(newv, choices)
								newv = v

							logging.debug("%s: oldval (%s) newval(%s)" % (name, oldv, newv))
							if oldv is None or (newv != "<keep>" and newv != oldv):
								self.cfg.setAttribute(cat, fn, name, newv)
								logging.debug("updated attributes")
					else:
						logging.debug("hidden attribute: %s" % name)

			if len(fskipped) > 0:
				skipped[fn] = fskipped

		if len(skipped) > 0:
			for fn in skipped:
				buf = ["%s:" % fn]
				for a in skipped[fn]:
					buf.append("    %s" % a)
				buf.append("")

				bufstr = "\n".join(buf)
				logging.debug("Attributes from map not saved because they did not appear in the ini file:")
				for b in buf:
					logging.debug(b)
				logging.debug("********************************************")

				dlg = wx.MessageDialog(self,
					"Attrubutes in map but not in ini file - skipping:\n" + bufstr,
					"Attributes skipped",
					wx.OK | wx.ICON_INFORMATION)
				dlg.ShowModal()
				dlg.Destroy()

		fl = self.cfg.writeModified()
		self.enablePendingChanges(False)

		if len(fl) == 0:
			dlg = wx.MessageDialog(self, "No files were saved", "No Files Saved", wx.OK | wx.ICON_INFORMATION)
		elif len(fl) == 1:
			dlg = wx.MessageDialog(self, "The following file was saved:\n%s" % fl[0], "File Saved",	wx.OK | wx.ICON_INFORMATION)
		else:
			dlg = wx.MessageDialog(self, "The following files were saved:\n%s" % "\n".join(fl), "Files Saved", wx.OK | wx.ICON_INFORMATION)

		dlg.ShowModal()
		dlg.Destroy()

	@staticmethod
	def getNewValue(name, attr, pgl, extGrpCount):
		results = []
		nms = []
		if extGrpCount > 0:
			for i in range(extGrpCount):
				nms.append(name + ("%d" % (i+1)))
		else:
			nms = [name]
			
		logging.debug("getnewvalue: names list = %s" % str(nms))
			
		for nm in nms:
			if pgl[nm] == "<keep>":
				newv = "<keep>"  # keep existing value
			elif attr["type"] == BOOLEAN:
				if pgl[nm] == 'True':
					logging.debug("string true for %s" % nm)
					newv = '1'
				elif pgl[nm] == 'False':
					logging.debug("string false for %s" % nm)
					newv = '0'
				else:
					logging.debug("true boolean value for %s" % nm)
					newv = '1' if pgl[nm] else '0'
			elif attr["type"] == COLORTYPE:
				hx = []
				print("try to convert %s to hex" % str(pgl[nm]), flush=True)
				for i in range(3):
					hx.append("%02X" % pgl[nm][i])
				newv = "".join(hx)
			else:
				newv = pgl[nm]
				
			results.append(newv)
			
		result = ",".join(results)
		logging.debug("getnewvalue result = (%s)" % result)
		return result
					
	def onCancel(self, _):
		if not self.verifyLoseChanges("cancel"):
			return 
		
		self.enablePendingChanges(False)
		if self.nchecked == 0:
			idxl = [self.lbFiles.GetSelection()]
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
		self.doReload()
		
	def doReload(self):
		self.cfg = CfgSlicer(self.settings.root, self.cats, self.attrMap)
		md = self.cfg.getMissingDirs()
		if len(md) > 0:
			self.parent.SetStatusText("Configuration directories missing: %s" % str(md))
			self.badConfig = True
		else:
			self.badConfig = False
			
		self.selected = None
		self.lbFiles.SetSelection(wx.NOT_FOUND)
		self.loadCategory(self.currentCategory)
		self.enablePendingChanges(False)
		self.allowCopy(False)
		self.allowDelete(False)
		
	def onBundle(self, _):
		dlg = BundleDlg(self, self.settings.root, self.cats)
		dlg.ShowModal()
		dlg.Destroy()
		
	def onUnbundle(self, _):
		dlg = UnBundleDlg(self, self.settings.root, self.cats)
		rc = dlg.ShowModal()
		nr = None
		if rc == wx.ID_OK:
			nr = dlg.getNewRoot()
			
		dlg.Destroy()
		
		if rc != wx.ID_OK:
			return 

		if nr is None:
			return
		
		self.settings.root = nr
		self.setTitle()
		self.settings.save()
		self.doReload()

	def onRoot(self, _):
		if self.propertiesChanged:
			if not self.verifyLoseChanges("switch to new root"):
				return 

		dlg = wx.DirDialog(self, "Choose a Slicer configuration directory:", style=wx.DD_DEFAULT_STYLE)		
		dlg.SetPath(self.settings.root)
		rc = dlg.ShowModal()
		newroot = None
		if rc == wx.ID_OK:
			newroot = dlg.GetPath()

		dlg.Destroy()
		if rc != wx.ID_OK:
			return
			
		fl = [f for f in os.listdir(newroot) if os.path.isdir(os.path.join(newroot, f))]
		missing = []
		for cat in self.cats:
			if cat not in fl:
				missing.append(cat)
				
		if len(missing) > 0:
			dlg = wx.MessageDialog(self,
					"The following subdirectories are missing: \n%s" % ",".join(missing),
					"Subdirectories missing",
					wx.OK | wx.ICON_ERROR)
			dlg.ShowModal()
			dlg.Destroy()
			return
		else:
			self.settings.root = newroot
			self.setTitle()		
			self.settings.save()
			
			self.doReload()
		
	def onAttrib(self, _):
		wildcard = "JSON (*.json)|*.json;*.JSON"
		
		abspath = os.path.abspath(self.settings.attrFile)
		
		d, f = os.path.split(abspath)
			
		dlg = wx.FileDialog(
			self, message="Choose a JSON-formatted attribute file",
			defaultDir=d, 
			defaultFile=f,
			wildcard=wildcard,
			style=wx.FD_OPEN)

		rc = dlg.ShowModal()
		
		if rc == wx.ID_OK:
			self.settings.attrFile = dlg.GetPath()
			
		dlg.Destroy()
		if rc != wx.ID_OK:
			return
		
		self.settings.save()
		
		self.restartRequired("Attribute map")

	def onVersion(self, _):
		self.attrMap.updateAttributeVersion(self.cfg.getSlicerVersion())
				
	def restartRequired(self, msg):
		dlg = wx.MessageDialog(self,
				"You must restart the program for this new %s to become effective" % msg,
				"Restart Required",
				wx.OK | wx.ICON_WARNING)
		dlg.ShowModal()
		dlg.Destroy()
				
	def okToClose(self):
		if self.propertiesChanged:
			if not self.verifyLoseChanges("exit"):
				return False
			
		return True
		
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
