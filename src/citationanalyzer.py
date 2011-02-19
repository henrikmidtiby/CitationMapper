#!/usr/bin/env python

import gtk
import gtk.gdk
import citationmapbuilder
import os
import StringIO
import re

import xdot

class MyDotWindow(xdot.DotWindow):
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


	def __init__(self):
		xdot.DotWindow.__init__(self)
		self.widget.connect('clicked', self.on_url_clicked)
		self.citationmap = citationmapbuilder.citationmapbuilder()

	def print_hello_world(self, widget):
		print "Hello World"

	def on_url_clicked(self, widget, url, event):
		dialog = gtk.MessageDialog(
				parent = self, 
				buttons = gtk.BUTTONS_OK,
				message_format="%s clicked" % url)
		dialog.connect('response', lambda dialog, response: dialog.destroy())
		dialog.run()
		return True

	def on_open(self, action):
		chooser = gtk.FileChooserDialog(title="Open directory with bibliography",
										action=gtk.FILE_CHOOSER_ACTION_SELECT_FOLDER,
										buttons=(gtk.STOCK_CANCEL,
												 gtk.RESPONSE_CANCEL,
												 gtk.STOCK_OPEN,
												 gtk.RESPONSE_OK))
		chooser.set_default_response(gtk.RESPONSE_OK)
		if chooser.run() == gtk.RESPONSE_OK:
			filename = chooser.get_filename()
			chooser.destroy()
			self.openfilename = filename
			self.open_directory(filename)
		else:
			chooser.destroy()


	def reload(self):
		if self.openfilename is not None:
			try:
				self.open_directory(self.openfilename)
			except IOError:
				pass


	def open_directory(self, directory):
		self.citationmap.__init__()
		files = os.listdir(directory)
		patterntxtfile = re.compile('.*\.txt')
		for file in files:
			res = patterntxtfile.match(file)
			if(res):
				self.citationmap.parsefile(os.path.join(directory, file))

		output = StringIO.StringIO()
		self.citationmap.analyzeGraph()
		self.citationmap.cleanUpGraph()
		self.citationmap.outputGraph(output)
		dotcode = output.getvalue()
		self.set_dotcode(dotcode)

		return True


dotcode = """
digraph G {
  Hello [URL="http://en.wikipedia.org/wiki/Hello"]
  World [URL="http://en.wikipedia.org/wiki/World"]
	Hello -> World
}
"""

def main():
	window = MyDotWindow()
	window.set_dotcode(dotcode)
	window.connect('destroy', gtk.main_quit)
	gtk.main()

if __name__ == '__main__':
	main()
