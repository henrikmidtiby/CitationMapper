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
import sys

import xdot
import citationmapbuilder

import GuiArticleDetails
import GuiListOfArticlesInGraph
import GuiOptionsWindow
import GuiArticleContextMenu
import GuiAboutDialog

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
				<menuitem action="Open"/>
				<menuitem action="Reload"/>
				<menuitem action="ExportToPDF"/>
				<menuitem action="Quit"/>
			</menu>
			<menu action="Help">
			<menuitem action="About"/>
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


		actiongroup.add_actions([
			('Quit', gtk.STOCK_QUIT, '_Quit', None, None, gtk.main_quit),
			('ExportToPDF', None, '_Export to pdf', 'E', None, self.exportToPDF),
			('About', None, '_About', None, None, self.showAboutDialog),
			('File', None, '_File'),
			('Help', None, '_Help')])

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

	def changeColorOfNode(self, url, newcolor):
		temp = self.mapview.graph
		for node in temp.nodes:
			if(isinstance(node, xdot.Node) and node.url == url):
				for shape in node.shapes:
					if(isinstance(shape, xdot.TextShape)):
						print(shape.t)
					if(isinstance(shape, xdot.EllipseShape)):
						shape.pen.fillcolor = newcolor
						shape.pen.color = newcolor
		self.mapview.queue_draw()

	def setupConnections(self):
		self.mapview.connect('clicked', self.articleClicked)
		self.citationmapperwindow.connect('destroy', gtk.main_quit)

	def articleClicked(self, widget, data, event):
		if(event.button == 1):
			self.on_url_clicked(widget, data, event)
			self.changeColorOfNode(data, (1, 0.75, 0.75, 1))
		else:
			articleContextMenu = GuiArticleContextMenu.GuiArticleContextMenu(self.openfilename)
			articleContextMenu.showContextMenu(widget, data, event)

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
		# Count the number of articles with the required number of references and citations.
		nNodes = 0
		for index in range(0, len(self.origNetworkCitations)):
			if(self.origNetworkCitations[index] >= self.minNumberOfCitations
					and self.origNetworkReferences[index] >= self.minNumberOfReferences):
				nNodes = nNodes + 1
		self.optionsWindow.graphSize = nNodes
		self.optionsWindow.labelGraphSize.set_text("Graph size: %d" % (nNodes))

	def showOptionsWindow(self):
		try:
			self.optionsWindow.searchoptionswindow.destroy()
		except:
			pass

		self.optionsWindow = GuiOptionsWindow.GuiOptionsWindow(self.maxCitations, self.maxReferences)
		self.optionsWindow.adjMinNumberOfReferences.connect("value_changed", self.updateMinNumberOfReferences)
		self.optionsWindow.adjMinNumberOfCitations.connect("value_changed", self.updateMinNumberOfCitations)
		self.optionsWindow.showgraphbutton.connect("clicked", self.filterAndShowCurrentCitationMap, None)
		self.optionsWindow.exportgraphbutton.connect("clicked", self.exportFilteredCitationMap, None)
		self.optionsWindow.listofnodesbutton.connect("clicked", self.getListOfNodes, None)
		self.optionsWindow.ignoreArticlesButton.connect("clicked", self.ignoreArticlesInBanFile, None)
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
			self.showOptionsWindow()
		else:
			chooser.destroy()

	def on_reload(self, action):
		if self.openfilename is not None:
			try:
				self.open_directory(self.openfilename)
				self.showOptionsWindow()
			except IOError:
				pass

	def open_directory(self, directory):
		self.openfilename = directory
		self.citationmap.__init__()
		files = os.listdir(directory)
		for file in files:
			print("Parsing file: %s" % file)
			self.citationmap.parsefile(os.path.join(directory, file))
		self.updateOrigNetwork()

	def updateOrigNetwork(self):
		self.origNetwork = self.citationmap.graph.copy()
		self.calculateNetworkProperties()

	def calculateNetworkProperties(self):
		self.origNetworkCitations = self.origNetwork.out_degree().values()
		self.origNetworkReferences = self.origNetwork.in_degree().values()
		try:
			self.maxCitations = max(self.origNetworkCitations)
			self.maxReferences = max(self.origNetworkReferences)
		except:
			self.maxCitations = 20
			self.maxReferences = 20

	def filterCurrentCitationMap(self):
		self.citationmap.graph = self.origNetwork.copy()
		self.citationmap.analyzeGraph()
		self.citationmap.cleanUpGraph(self.minNumberOfReferences, self.minNumberOfCitations)

	def filterAndExportCurrentCitationMap(self):
		self.filterCurrentCitationMap()
		output = StringIO.StringIO()
		self.citationmap.outputGraph(output, "BT")
		dotcode = output.getvalue()
		return dotcode

	def filterAndShowCurrentCitationMap(self, action, data):
		if(self.optionsWindow.graphSize > 200):
			if(not self.dialogShowLargeGraph(self.optionsWindow.graphSize)):
				return
		dotcode = self.filterAndExportCurrentCitationMap()
		self.mapview.set_dotcode(dotcode)
		self.mapview.zoom_to_fit()

	def dialogShowLargeGraph(self, nNodes):
		self.quit_dialog = gtk.Dialog()

		# Set it modal and transient for main window.
		self.quit_dialog.set_modal( True )
		#self.quit_dialog.set_transient_for( self )

		# Set title
		self.quit_dialog.set_title( 'Confirmation' )

		# Add buttons.
		self.quit_dialog.add_button( gtk.STOCK_YES, 1 )
		self.quit_dialog.add_button( gtk.STOCK_NO,  2 )

		'''
		# Using non-null parameter list when creating dialog,
		# the last six calls can be written as:
		self.quit_dialog = gtk.Dialog( 'Conformation', self,
									   gtk.DIALOG_MODAL,
									   ( gtk.STOCK_YES, 1,
										 gtk.STOCK_NO,  2 ) )
		'''

		# Create label
		label = gtk.Label( 'Will you really visualize this huge graph? (# nodes = %d)' % nNodes )

		self.quit_dialog.vbox.pack_start( label )

		# Show dialog
		self.quit_dialog.show_all()

		# Run dialog
		response = self.quit_dialog.run()
		self.quit_dialog.hide()

		return(response == 1)


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
				networkCitations = self.origNetwork.out_degree(key)
				networkReferences = self.origNetwork.in_degree(key)
				article = self.citationmap.articles[key]
				year = int(article['PY'][0])
				SO = string.join(article['SO'])
				Title = string.join(article['TI'])
				Authors = string.join(article['AU'], ' and ')
				TC = int(article['TC'][0])
				NR = int(article['NR'][0])
				piter = listOfNodes.nodesTreestore.append(None, [key, year, networkCitations, networkReferences, TC, NR, SO, Authors, Title])
			except:
				piter = listOfNodes.nodesTreestore.append(None, [key, 0, networkCitations, networkReferences, 0, 0, "", "", ""])
				pass

	def ignoreArticlesInBanFile(self, action, data):
		filename = "%s/banlist" % self.openfilename 
		try:
			fh = open(filename)
			for line in fh:
				articleIdentifier = line[:-1]
				try:
					self.origNetwork.remove_node(articleIdentifier)
				except:
					pass
		except:
			pass
		self.calculateNetworkProperties()
		self.showOptionsWindow()

	def showAboutDialog(self, action):
		gad = GuiAboutDialog.GuiAboutDialog()

	def exportToPDF(self, action):
		chooser = gtk.FileChooserDialog(title=None,action=gtk.FILE_CHOOSER_ACTION_SAVE,
						buttons=(gtk.STOCK_CANCEL,gtk.RESPONSE_CANCEL,gtk.STOCK_SAVE,gtk.RESPONSE_OK))
		if chooser.run() == gtk.RESPONSE_OK:
			filename = chooser.get_filename()
			chooser.destroy()
			self.mapview.exportToPDF(filename)
		else:
			chooser.destroy()
		return False


def main():
	gmw = GuiMainWindow()

	if(len(sys.argv) > 1):
		gmw.open_directory(sys.argv[1])
		gmw.showOptionsWindow()

	gtk.main()

if __name__ == '__main__':
	main()

