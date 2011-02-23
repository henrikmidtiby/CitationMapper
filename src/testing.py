#!/usr/bin/env python

import gtk
import gtk.gdk
import gobject
import xdot

class CitationAnalyzerMainWindow():
	ui = '''
	<ui>
		<toolbar name="ToolBar">
			<toolitem action="Open"/>
			<toolitem action="Reload"/>
			<separator/>
			<toolitem action="ZoomIn"/>
			<toolitem action="ZoomOut"/>
			<toolitem action="ZoomFit"/>
			<toolitem action="Zoom100"/>
		</toolbar>
	</ui>
	'''
	
	dotcode = """
	digraph G {
	  Hello [URL="http://en.wikipedia.org/wiki/Hello"]
	  World [URL="http://en.wikipedia.org/wiki/World"]
		Hello -> World
	}
	"""

	def startTwo(self):
		self.window = gtk.Window()
		vbox = gtk.VBox()
		self.window.add(vbox)

		self.uimanager = gtk.UIManager()
		self.actiongroup = gtk.ActionGroup('Actions')
		# Create actions
		self.actiongroup.add_actions((
			('Open', gtk.STOCK_OPEN, None, None, None, self.emptyFunction),
			('Reload', gtk.STOCK_REFRESH, None, None, None, self.emptyFunction),
			('ZoomIn', gtk.STOCK_ZOOM_IN, None, None, None, self.emptyFunction),
			('ZoomOut', gtk.STOCK_ZOOM_OUT, None, None, None, self.emptyFunction),
			('ZoomFit', gtk.STOCK_ZOOM_FIT, None, None, None, self.emptyFunction),
			('Zoom100', gtk.STOCK_ZOOM_100, None, None, None, self.emptyFunction),
		))
		self.uimanager.insert_action_group(self.actiongroup, 0)
		self.uimanager.add_ui_from_string(self.ui)
		toolbar = self.uimanager.get_widget('/ToolBar')
		vbox.pack_start(toolbar, False)
		vbox.show()
		self.window.show()

	def emptyFunction(self, widget=None, url=None, event=None):
		pass


	def start(self):
		self.window = gtk.Window()
		self.window.set_default_size(512, 512)
		self.vbox = gtk.VBox()

		# Add test label
		self.labelReferences = gtk.Label("Number of references")
		self.labelReferences.show()
		self.vbox.pack_start(self.labelReferences, False, True, 0)

		# Add graph widget
		self.graphwidget = xdot.DotWidget()
		self.graphwidget.connect('clicked', self.emptyFunction)
		self.graphwidget.set_dotcode(self.dotcode)
		self.graphwidget.show()
		self.vbox.pack_start(self.graphwidget, True, True, 0)

		self.window.add(self.vbox)
		self.graphwidget.zoom_to_fit()
		self.vbox.show()
		self.window.show()


def main():
	camw = CitationAnalyzerMainWindow()
	camw.start()
	camw.window.connect('destroy', gtk.main_quit)

	gtk.main()

main()
