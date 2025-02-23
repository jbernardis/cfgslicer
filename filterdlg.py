import wx
import json


class FilterDlg(wx.Dialog):
	def __init__(self, parent, files, attrmap, config, category):
		wx.Dialog.__init__(self, parent, wx.ID_ANY, "Set filter for category %s" % category)
		self.Bind(wx.EVT_CLOSE, self.onCancel)
		self.parent = parent
		self.files = files
		self.attrMap = attrmap
		self.cfg = config
		self.cat = category

		self.selection = wx.NOT_FOUND
		self.attrName = None
		self.attrType = None
		self.attrValue = ""

		grps = self.attrMap.getGroups(self.cat)
		self.attrs = []
		for g in grps:
			self.attrs.extend([a for a in self.attrMap.getGroupAttrs(self.cat, g) if "name" in a])

		#  print("attributes: %s" % json.dumps(self.attrs, indent=2))
		self.attrList = sorted([a["name"] for a in self.attrs if a["type"] not in ["hidden", "color"]])
		self.attrNameMap = {a["name"]: a for a in self.attrs}
		self.lbAttr = wx.ListBox(self, wx.ID_ANY, choices=self.attrList)
		if len(self.attrList) == 0:
			self.selection = wx.NOT_FOUND
			self.attrName = None
			self.attrType = None
		else:
			self.selection = 0
			self.attrName = self.attrList[0]
			self.attrType = self.attrNameMap[self.attrName]["type"]

		self.lbAttr.SetSelection(self.selection)
		self.Bind(wx.EVT_LISTBOX, self.onLbAttr, self.lbAttr)

		self.bValue = wx.Button(self, wx.ID_ANY, "Set Value")
		self.bValue.Enable(self.selection != wx.NOT_FOUND)
		self.Bind(wx.EVT_BUTTON, self.onBValue, self.bValue)

		self.stValue = wx.StaticText(self, wx.ID_ANY, "", size=[300, -1])

		self.bOK = wx.Button(self, wx.ID_ANY, "OK")
		self.bOK.Enable(False)
		self.Bind(wx.EVT_BUTTON, self.onBOK, self.bOK)

		self.bCancel = wx.Button(self, wx.ID_ANY, "Cancel")
		self.Bind(wx.EVT_BUTTON, self.onCancel, self.bCancel)

		vsz = wx.BoxSizer(wx.VERTICAL)
		vsz.AddSpacer(20)
		vsz.Add(self.lbAttr, 0, wx.ALIGN_CENTER_HORIZONTAL)
		vsz.AddSpacer(20)

		hsz = wx.BoxSizer(wx.HORIZONTAL)
		hsz.Add(self.bValue)
		hsz.AddSpacer(20)
		hsz.Add(self.stValue)

		vsz.Add(hsz, 0, wx.ALIGN_CENTER_HORIZONTAL)
		vsz.AddSpacer(20)

		hsz = wx.BoxSizer(wx.HORIZONTAL)
		hsz.Add(self.bOK)
		hsz.AddSpacer(30)
		hsz.Add(self.bCancel)
		vsz.Add(hsz, 0, wx.ALIGN_CENTER_HORIZONTAL)
		vsz.AddSpacer(20)

		hsz = wx.BoxSizer(wx.HORIZONTAL)
		hsz.AddSpacer(20)
		hsz.Add(vsz)
		hsz.AddSpacer(20)

		self.SetSizer(hsz)
		self.Layout()
		self.Fit()

	def onLbAttr(self, _):
		self.selection = self.lbAttr.GetSelection()
		self.bValue.Enable(self.selection != wx.NOT_FOUND)
		if self.selection == wx.NOT_FOUND:
			self.attrName = None
			self.attrType = None
			return

		self.stValue.SetLabel("")
		self.attrValue = ""
		self.attrName = self.lbAttr.GetString(self.selection)
		try:
			self.attrType = self.attrNameMap[self.attrName]["type"]
		except KeyError:
			self.attrType = "string"

	def onBValue(self, _):
		if self.attrMap.IsChoiceType(self.attrType):
			choices = sorted([c[1] for c in self.attrMap.getChoices(self.attrType)])
			dlg = wx.SingleChoiceDialog(self, "choose value", self.attrName,
				choices, wx.CHOICEDLG_STYLE)
			rc = dlg.ShowModal()
			if rc == wx.ID_OK:
				self.attrValue = dlg.GetStringSelection()
			else:
				self.attrValue = None
			dlg.Destroy()
		elif self.attrType == "boolean":
			dlg = wx.SingleChoiceDialog(self, "choose value", self.attrName,
				["True", "False"], wx.CHOICEDLG_STYLE)
			rc = dlg.ShowModal()
			if rc == wx.ID_OK:
				self.attrValue = dlg.GetStringSelection()
			else:
				self.attrValue = None
			dlg.Destroy()

		else:
			self.attrValue = "123"

		self.bOK.Enable(self.attrValue is not None)
		self.stValue.SetLabel("" if self.attrValue is None else self.attrValue)

	def getResults(self):
		results = []
		if self.attrType == "boolean":
			av = "0" if self.attrValue == "False" else "1"
		else:
			av = self.attrValue

		for fx in range(len(self.files)):
			fl = self.files[fx]
			fv = self.cfg.getAttribute(self.cat, fl, self.attrName)
			if self.attrType == "boolean":
				print("compare %s %s to %s %s" % (fv, type(fv), av, type(av)))
			if fv == av:
				results.append(fx)
		return results

	def onBOK(self, _):
		self.doClose(wx.ID_OK)

	def onCancel(self, evt):
		self.doClose(wx.ID_CANCEL)

	def doClose(self, rc):
		self.EndModal(rc)


