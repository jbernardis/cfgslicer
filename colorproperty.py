import wx
import wx.propgrid as wxpg

from cfgexceptions import CfgInvalidColor
from helpers import parseColorValue


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
