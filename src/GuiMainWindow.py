#-------------------------------------------------------------------------------
# Name:        GuiMainWindow
# Purpose:     Main window for the citation mapper program
#
# Author:      Henrik Skov Midtiby
#
# Created:     2011-02-25
# Copyright:   (c) Henrik Skov Midtiby 2011
# Licence:     <your licence>
#-------------------------------------------------------------------------------
#!/usr/bin/env python

import os
import re
import gtk
import StringIO
import pprint

import xdot
import citationmapbuilder

import GuiArticleDetails
import GuiListOfArticlesInGraph
import GuiOptionsWindow
import GuiArticleContextMenu

class GuiMainWindow:
	dotcode = """
	digraph G {
	  Hello [URL="http://en.wikipedia.org/wiki/Hello"]
	  World [URL="http://en.wikipedia.org/wiki/World"]
		Hello -> World
	}
	"""

	ui = '''
	<ui>
		<menubar name="MenuBar">
			<menu action="File">
				<menuitem action="Quit"/>
			</menu>
		</menubar>
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

	openfilename = None
	minNumberOfReferences = 1
	minNumberOfCitations = 3


	def __init__(self):
		self.setupWindowContents()
		self.setupConnections()
		self.citationmap = citationmapbuilder.citationmapbuilder()

	def setupWindowContents(self):
		self.citationmapperwindow = gtk.Window()
		self.citationmapperwindow.set_title("Citation mapper")
		self.citationmapperwindow.set_size_request(500, 200)

		# Create a UIManager instance
		uimanager = self.uimanager = gtk.UIManager()

		# Outer vertical box
		vbox = gtk.VBox(False, 0)

		# Label
		labelReferences = gtk.Label("Number of references")

		# Network window
		self.mapview = xdot.DotWidget()

		# Action bar
		# Create an ActionGroup
		actiongroup = gtk.ActionGroup('Actions')
		self.actiongroup = actiongroup

		# Create actions
		actiongroup.add_actions((
			('Open', gtk.STOCK_OPEN, None, None, None, self.on_open),
			('Reload', gtk.STOCK_REFRESH, None, None, None, self.on_reload),
			('ZoomIn', gtk.STOCK_ZOOM_IN, None, None, None, self.mapview.on_zoom_in),
			('ZoomOut', gtk.STOCK_ZOOM_OUT, None, None, None, self.mapview.on_zoom_out),
			('ZoomFit', gtk.STOCK_ZOOM_FIT, None, None, None, self.mapview.on_zoom_fit),
			('Zoom100', gtk.STOCK_ZOOM_100, None, None, None, self.mapview.on_zoom_100),
		))


		actiongroup.add_actions([('Quit', gtk.STOCK_QUIT, '_Quit me!', None,
			'Quit the Program', gtk.main_quit),
			('File', None, '_File')])

		# Add the actiongroup to the uimanager
		uimanager.insert_action_group(actiongroup, 0)

		# Add the accelerator group to the toplevel window
		accelgroup = uimanager.get_accel_group()
		self.citationmapperwindow.add_accel_group(accelgroup)



		# Add a UI descrption
		uimanager.add_ui_from_string(self.ui)

		# Create a menu
		menuline = uimanager.get_widget('/MenuBar')
		vbox.pack_start(menuline, False)

		# Create a Toolbar
		toolbar = uimanager.get_widget('/ToolBar')
		vbox.pack_start(toolbar, False)
		#vbox.pack_start(labelReferences, False, True, 0)
		vbox.pack_start(self.mapview, True, True, 0)

		vbox.show_all()
		self.citationmapperwindow.add(vbox)
		self.citationmapperwindow.show()

		self.mapview.set_dotcode(self.dotcode)

	def printNodeInformation(self):
		return
		temp = self.mapview.graph
		pp = pprint.PrettyPrinter()
		#for shape in temp.shapes:
		#	pp.pprint(shape)
		#for edge in temp.edges:
		#	pp.pprint(edge)
		for node in temp.nodes:
			for shape in node.shapes:
				if(isinstance(shape, xdot.TextShape)):
					print(shape.t)
				if(isinstance(shape, xdot.EllipseShape)):
					shape.pen.fillcolor = (1, 0, 1, 1)
					shape.pen.color = (1, 0, 1, 1)

	def changeColorOfNode(self, url, newcolor):
		temp = self.mapview.graph
		for node in temp.nodes:
			if(len(node.shapes) == 2):
				if(isinstance(node.shapes[1], xdot.TextShape)
						and node.shapes[1].t == url):
					node.shapes[0].pen.color = newcolor
					node.shapes[0].pen.fillcolor = newcolor
			if(len(node.shapes) == 3):
				if(isinstance(node.shapes[2], xdot.TextShape)
						and node.shapes[2].t == url):
					node.shapes[0].pen.color = newcolor
					node.shapes[0].pen.fillcolor = newcolor
		self.mapview.queue_draw()

	def setupConnections(self):
		self.mapview.connect('clicked', self.articleClicked)
		self.citationmapperwindow.connect('destroy', gtk.main_quit)

	def articleClicked(self, widget, data, event):
		if(event.button == 1):
			print(data)
			self.on_url_clicked(widget, data, event)
			self.changeColorOfNode(data, (1, 0.5, 0.5, 1))
		else:
			articleContextMenu = GuiArticleContextMenu.GuiArticleContextMenu()
			articleContextMenu.showContextMenu(widget, data, event)
			self.printNodeInformation()

	def __init__old(self):
		xdot.DotWindow.__init__(self)

	def on_url_clicked(self, widget, url, event):
		self.articleDetailsWindow = GuiArticleDetails.GuiArticleDetails()
		try:
			article = self.citationmap.articles[url]
			graph = self.citationmap.graph
			self.articleDetailsWindow.updateArticleInformation(url, article, graph)
		except:
			self.articleDetailsWindow.updateArticleInformation(url)

	def updateMinNumberOfReferences(self, adj):
		self.minNumberOfReferences = adj.value
		self.calculateNewGraphSizeAndUpdateOptionsWindow()

	def updateMinNumberOfCitations(self, adj):
		self.minNumberOfCitations = adj.value
		self.calculateNewGraphSizeAndUpdateOptionsWindow()

	def calculateNewGraphSizeAndUpdateOptionsWindow(self):
		self.filterCurrentCitationMap()
		nNodes = self.citationmap.graphForAnalysis.number_of_nodes()
		nEdges = self.citationmap.graphForAnalysis.number_of_edges()
		self.optionsWindow.labelGraphSize.set_text("Graph size: %d / %d" % (nNodes, nEdges))

	def showOptionsWindow(self):
		self.optionsWindow = GuiOptionsWindow.GuiOptionsWindow()
		self.optionsWindow.adjMinNumberOfReferences.connect("value_changed", self.updateMinNumberOfReferences)
		self.optionsWindow.adjMinNumberOfCitations.connect("value_changed", self.updateMinNumberOfCitations)
		self.optionsWindow.showgraphbutton.connect("clicked", self.filterAndShowCurrentCitationMap, None)
		self.optionsWindow.exportgraphbutton.connect("clicked", self.exportFilteredCitationMap, None)
		self.optionsWindow.listofnodesbutton.connect("clicked", self.getListOfNodes, None)
		self.calculateNewGraphSizeAndUpdateOptionsWindow()

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
		self.origNetwork = self.citationmap.graph.copy()

	def filterCurrentCitationMap(self):
		self.citationmap.graph = self.origNetwork.copy()
		self.citationmap.analyzeGraph()
		self.citationmap.cleanUpGraph(self.minNumberOfReferences, self.minNumberOfCitations)

	def filterAndExportCurrentCitationMap(self):
		self.filterCurrentCitationMap()
		output = StringIO.StringIO()
		self.citationmap.outputGraph(output)
		dotcode = output.getvalue()
		return dotcode

	def filterAndShowCurrentCitationMap(self, action, data):
		dotcode = self.filterAndExportCurrentCitationMap()
		self.mapview.set_dotcode(dotcode)
		self.mapview.zoom_to_fit()

	def exportFilteredCitationMap(self, action, data):
		chooser = gtk.FileChooserDialog(title=None,action=gtk.FILE_CHOOSER_ACTION_SAVE,
						buttons=(gtk.STOCK_CANCEL,gtk.RESPONSE_CANCEL,gtk.STOCK_SAVE,gtk.RESPONSE_OK))
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
		listOfNodes = GuiListOfArticlesInGraph.GuiListOfArticlesInGraph()
		self.filterCurrentCitationMap()
		listOfNodes.nodesTreestore.clear()
		for key in self.citationmap.graphForAnalysis.nodes():
			try:
				article = self.citationmap.articles[key]
				year = int(article['PY'][0])
				TC = int(article['TC'][0])
				NR = int(article['NR'][0])
				piter = listOfNodes.nodesTreestore.append(None, [key, year, TC, NR])
			except:
				pass

def main():
	gmw = GuiMainWindow()
	gtk.main()

if __name__ == '__main__':
    main()