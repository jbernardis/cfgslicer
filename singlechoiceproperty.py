import wx
import wx.propgrid as wxpg


def ValueToChoice(val, choices):
	for c, v in choices:
		if val == v:
			return c
	return val


def ChoiceToValue(choice, choices):
	for c, v in choices:
		if choice == c:
			return v
	return choice


class SingleChoiceDialogAdapter(wxpg.PGEditorDialogAdapter):
	def __init__(self, prop, choices, message, caption):
		wxpg.PGEditorDialogAdapter.__init__(self)
		self.prop = prop
		self.choices = [x[0] for x in choices]
		self.values = [x[1] for x in choices]
		self.message = message
		self.caption = caption

	def DoShowDialog(self, propGrid, _):
		cv = self.prop.GetValue()
		try:
			idx = self.choices.index(cv)
		except (KeyError, IndexError):
			idx = 0
		
		s = wx.GetSingleChoice(self.message, self.caption, self.choices, idx)
		
		if s:
			sx = self.choices.index(s)
			self.SetValue(self.choices[sx])
			return True
		
		return False


class SingleChoiceProperty(wxpg.StringProperty):
	def __init__(self, label, name, value, choices, message, caption):
		c = ValueToChoice(value, choices)
		wxpg.StringProperty.__init__(self, label, name, c)
		self.dialog_choices = [x for x in choices]
		self.message = message
		self.caption = caption

	def DoGetEditorClass(self):
		return wxpg.PropertyGridInterface.GetEditorByName("TextCtrlAndButton")

	def GetEditorDialog(self):
		return SingleChoiceDialogAdapter(self, self.dialog_choices, self.message, self.caption)
