#!/usr/bin/env python

import gtk
import gtk.gdk
import citationmapbuilder
import os
import StringIO
import re
import sys

import xdot

class MyDotWindow(xdot.DotWindow):
	minNumberOfReferences = 1
	minNumberOfCitations = 3

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

	def on_url_clicked(self, widget, url, event):
		tempwindow = gtk.Window()
		text = gtk.TextView()
		tempwindow.add(text)
		text.show()
		tempwindow.show()

		try:
			author = self.citationmap.articles[url]["AU"]
			year = self.citationmap.articles[url]["PY"]
			title = self.citationmap.articles[url]["TI"]
			nreferences = self.citationmap.articles[url]["NR"]
			ncitations = self.citationmap.articles[url]["TC"]
			text.get_buffer().insert_at_cursor('%s\n' % author)
			text.get_buffer().insert_at_cursor('%s\n' % year)
			text.get_buffer().insert_at_cursor('%s\n' % title)
			text.get_buffer().insert_at_cursor('Number of references: %s\n' % nreferences)
			text.get_buffer().insert_at_cursor('Times cited: %s\n' % ncitations)
		except:
			text.get_buffer().insert_at_cursor('%s\n' % url)

		return True

	def updateMinNumberOfReferences(self, adj):
		self.minNumberOfReferences = adj.value

	def updateMinNumberOfCitations(self, adj):
		self.minNumberOfCitations = adj.value

	def showOptionsWindow(self):
		tempwindow = gtk.Window()
		vbox = gtk.VBox(False, 0)
		tempwindow.add(vbox)
		adjMinNumberOfReferences = gtk.Adjustment(value=self.minNumberOfReferences, lower=0, upper=20, step_incr=1, page_incr=5, page_size=0)
		adjMinNumberOfReferences.connect("value_changed", self.updateMinNumberOfReferences)
		hscrollbarReferences = gtk.HScale(adjMinNumberOfReferences)
		hscrollbarReferences.set_digits(0)
		hscrollbarReferences.set_value_pos(gtk.POS_LEFT)
		adjMinNumberOfCitations = gtk.Adjustment(value=self.minNumberOfCitations, lower=0, upper=20, step_incr=1, page_incr=5, page_size=0)
		adjMinNumberOfCitations.connect("value_changed", self.updateMinNumberOfCitations)
		hscrollbarCitations = gtk.HScale(adjMinNumberOfCitations)
		hscrollbarCitations.set_digits(0)
		hscrollbarCitations.set_value_pos(gtk.POS_LEFT)
		tempbutton = gtk.Button("Show graph")
		labelReferences = gtk.Label("Number of references")
		labelCitations = gtk.Label("Number of citations")
		tempbutton.connect("clicked", self.filterAndShowCurrentCitationMap, None)
		tempbutton.show()
		labelReferences.show()
		labelCitations.show()
		hscrollbarReferences.show()
		hscrollbarCitations.show()
		vbox.pack_start(labelReferences, True, True, 0)
		vbox.pack_start(hscrollbarReferences, True, True, 0)
		vbox.pack_start(labelCitations, True, True, 0)
		vbox.pack_start(hscrollbarCitations, True, True, 0)
		vbox.pack_start(tempbutton, True, True, 0)
		vbox.show()
		tempwindow.show()

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

		self.showOptionsWindow()


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
			#if(res):
			self.citationmap.parsefile(os.path.join(directory, file))

	def filterAndShowCurrentCitationMap(self, action, data):
		output = StringIO.StringIO()
		origNetwork = self.citationmap.graph.copy()
		self.citationmap.analyzeGraph()
		self.citationmap.cleanUpGraph(self.minNumberOfReferences, self.minNumberOfCitations)
		self.citationmap.outputGraph(output)
		dotcode = output.getvalue()
		self.set_dotcode(dotcode)
		self.citationmap.graph = origNetwork

		return False


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
	window.showOptionsWindow()
	if(len(sys.argv) > 1):
		window.open_directory(sys.argv[1])

	gtk.main()

if __name__ == '__main__':
	main()
