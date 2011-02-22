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
		nodeinformationwindow = gtk.Window()
		text = gtk.TextView()
		nodeinformationwindow.add(text)
		text.show()
		nodeinformationwindow.show()

		try:
			author = self.citationmap.articles[url]["AU"]
			year = self.citationmap.articles[url]["PY"]
			title = self.citationmap.articles[url]["TI"]
			nreferences = self.citationmap.articles[url]["NR"]
			nreferencesInGraph = self.citationmap.graph.in_degree(url)
			ncitations = self.citationmap.articles[url]["TC"]
			ncitationsInGraph = self.citationmap.graph.out_degree(url)
			text.get_buffer().insert_at_cursor('%s\n' % url)
			text.get_buffer().insert_at_cursor('%s\n' % author)
			text.get_buffer().insert_at_cursor('%s\n' % year)
			text.get_buffer().insert_at_cursor('%s\n' % title)
			text.get_buffer().insert_at_cursor('Number of references: %s (%s)\n' % (nreferences, nreferencesInGraph))
			text.get_buffer().insert_at_cursor('Times cited: %s (%s)\n' % (ncitations, ncitationsInGraph))
		except:
			text.get_buffer().insert_at_cursor('%s\n' % url)

		return True

	def updateMinNumberOfReferences(self, adj):
		self.minNumberOfReferences = adj.value

	def updateMinNumberOfCitations(self, adj):
		self.minNumberOfCitations = adj.value

	def showOptionsWindow(self):
		searchoptionswindow = gtk.Window()
		searchoptionswindow.set_border_width(10)
		vbox = gtk.VBox(False, 0)
		searchoptionswindow.add(vbox)
		adjMinNumberOfReferences = gtk.Adjustment(value=self.minNumberOfReferences, lower=0, upper=50, step_incr=1, page_incr=5, page_size=0)
		adjMinNumberOfReferences.connect("value_changed", self.updateMinNumberOfReferences)
		hscrollbarReferences = gtk.HScale(adjMinNumberOfReferences)
		hscrollbarReferences.set_digits(0)
		hscrollbarReferences.set_value_pos(gtk.POS_LEFT)
		adjMinNumberOfCitations = gtk.Adjustment(value=self.minNumberOfCitations, lower=0, upper=50, step_incr=1, page_incr=5, page_size=0)
		adjMinNumberOfCitations.connect("value_changed", self.updateMinNumberOfCitations)
		hscrollbarCitations = gtk.HScale(adjMinNumberOfCitations)
		hscrollbarCitations.set_digits(0)
		hscrollbarCitations.set_value_pos(gtk.POS_LEFT)
		showgraphbutton = gtk.Button("Show graph")
		exportgraphbutton = gtk.Button("Export graph")
		listofnodesbutton = gtk.Button("Get list of nodes")
		labelReferences = gtk.Label("Number of references")
		labelCitations = gtk.Label("Number of citations")
		showgraphbutton.connect("clicked", self.filterAndShowCurrentCitationMap, None)
		exportgraphbutton.connect("clicked", self.exportFilteredCitationMap, None)
		listofnodesbutton.connect("clicked", self.getListOfNodes, None)
		showgraphbutton.show()
		exportgraphbutton.show()
		listofnodesbutton.show()
		labelReferences.show()
		labelCitations.show()
		hscrollbarReferences.show()
		hscrollbarCitations.show()
		vbox.pack_start(labelReferences, True, True, 0)
		vbox.pack_start(hscrollbarReferences, True, True, 0)
		vbox.pack_start(labelCitations, True, True, 0)
		vbox.pack_start(hscrollbarCitations, True, True, 0)
		vbox.pack_start(showgraphbutton, True, True, 0)
		vbox.pack_start(exportgraphbutton, True, True, 0)
		vbox.pack_start(listofnodesbutton, True, True, 0)
		vbox.show()
		searchoptionswindow.show()

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
			self.open_directory(filename)
		else:
			chooser.destroy()

		self.showOptionsWindow()


	def on_reload(self, action):
		print("Reload pressed")
		if self.openfilename is not None:
			try:
				self.open_directory(self.openfilename)
			except IOError:
				pass


	def open_directory(self, directory):
		self.openfilename = directory
		self.citationmap.__init__()
		files = os.listdir(directory)
		patterntxtfile = re.compile('.*\.txt')
		for file in files:
			res = patterntxtfile.match(file)
			#if(res):
			self.citationmap.parsefile(os.path.join(directory, file))

	def filterAndExportCurrentCitationMap(self):
		output = StringIO.StringIO()
		origNetwork = self.citationmap.graph.copy()
		self.citationmap.analyzeGraph()
		self.citationmap.cleanUpGraph(self.minNumberOfReferences, self.minNumberOfCitations)
		self.citationmap.outputGraph(output)
		dotcode = output.getvalue()
		self.citationmap.graph = origNetwork
		return dotcode

	def filterAndShowCurrentCitationMap(self, action, data):
		dotcode = self.filterAndExportCurrentCitationMap()
		self.set_dotcode(dotcode)

	def exportFilteredCitationMap(self, action, data):
		chooser = gtk.FileChooserDialog(title=None,action=gtk.FILE_CHOOSER_ACTION_SAVE,
						buttons=(gtk.STOCK_CANCEL,gtk.RESPONSE_CANCEL,gtk.STOCK_OPEN,gtk.RESPONSE_OK))
		if chooser.run() == gtk.RESPONSE_OK:
			filename = chooser.get_filename()
			chooser.destroy()

			exportfile = open(filename, 'w')
			dotcode = self.filterAndExportCurrentCitationMap()
			exportfile.write(dotcode)
			exportfile.close()

		else:
			chooser.destroy()
		return False

	def getListOfNodes(self, action, data):
		nodewindow = gtk.Window(gtk.WINDOW_TOPLEVEL)

		nodewindow.set_title("Basic TreeView Example")

		nodewindow.set_size_request(200, 200)

		# create a TreeStore with one string column to use as the model
		nodesTreestore = gtk.TreeStore(str, str)

		# we'll add some data now - 4 rows with 3 child rows each
		for parent in range(4):
			piter = nodesTreestore.append(None, ['parent %i' % parent, 'test'])

		# create the TreeView using treestore
		nodesTreeview = gtk.TreeView(nodesTreestore)

		# create the TreeViewColumn to display the data
		columnOne = gtk.TreeViewColumn('Column 0')
		columnTwo = gtk.TreeViewColumn('Column 2')

		# add tvcolumn to treeview
		nodesTreeview.append_column(columnOne)
		nodesTreeview.append_column(columnTwo)

		# create a CellRendererText to render the data
		cellRenderer = gtk.CellRendererText()

		# add the cell to the tvcolumn and allow it to expand
		columnOne.pack_start(cellRenderer, True)
		columnTwo.pack_start(cellRenderer, True)

		# set the cell "text" attribute to column 0 - retrieve text
		# from that column in treestore
		columnOne.add_attribute(cellRenderer, 'text', 0)
		columnTwo.add_attribute(cellRenderer, 'text', 1)

		# make it searchable
		nodesTreeview.set_search_column(0)

		# Allow sorting on the column
		columnOne.set_sort_column_id(0)

		# Allow drag and drop reordering of rows
		nodesTreeview.set_reorderable(True)

		nodewindow.add(nodesTreeview)

		nodewindow.show_all()

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
