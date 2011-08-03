#-------------------------------------------------------------------------------
# Name:        GuiOptionsWindow
# Purpose:     Graph showing options window for the citation mapper program
#
# Author:      Henrik Skov Midtiby
#
# Created:     2011-02-25
# Copyright:   (c) Henrik Skov Midtiby 2011
# Licence:     <your licence>
#-------------------------------------------------------------------------------
#!/usr/bin/env python

import gtk

class GuiOptionsWindow:
	minNumberOfReferences = 1
	minNumberOfCitations = 3

	def __init__(self, maxCitations=50, maxReferences=50):
		searchoptionswindow = gtk.Window()
		searchoptionswindow.set_border_width(10)
		self.vbox = gtk.VBox(False, 0)
		searchoptionswindow.add(self.vbox)
		self.adjMinNumberOfReferences = gtk.Adjustment(value=self.minNumberOfReferences, lower=0, upper=maxReferences, step_incr=1, page_incr=5, page_size=0)
		self.hscrollbarReferences = gtk.HScale(self.adjMinNumberOfReferences)
		self.hscrollbarReferences.set_digits(0)
		self.hscrollbarReferences.set_value_pos(gtk.POS_LEFT)
		labelReferences = gtk.Label("Number of references")
		labelCitations = gtk.Label("Number of citations")
		labelReferences.show()
		labelCitations.show()
		self.hscrollbarReferences.show()
		self.vbox.pack_start(labelReferences, True, True, 0)
		self.vbox.pack_start(self.hscrollbarReferences, True, True, 0)
		self.vbox.pack_start(labelCitations, True, True, 0)
		self.addHscrollbarCitations(maxCitations)
		self.addLabelGraphSize()
		self.addShowGraphButton()
		self.addExportGraphButton()
		self.addListOfNodesButton()
		self.vbox.show()
		searchoptionswindow.show()

	def addHscrollbarCitations(self, maxCitations):
		self.adjMinNumberOfCitations = gtk.Adjustment(value=self.minNumberOfCitations, lower=0, upper=maxCitations, step_incr=1, page_incr=5, page_size=0)
		self.hscrollbarCitations = gtk.HScale(self.adjMinNumberOfCitations)
		self.hscrollbarCitations.set_digits(0)
		self.hscrollbarCitations.set_value_pos(gtk.POS_LEFT)
		self.hscrollbarCitations.show()
		self.vbox.pack_start(self.hscrollbarCitations, True, True, 0)

	def addLabelGraphSize(self):
		self.labelGraphSize = gtk.Label("Graph size: nodes")
		self.labelGraphSize.show()
		self.vbox.pack_start(self.labelGraphSize, True, True, 0)

	def addShowGraphButton(self):
		self.showgraphbutton = gtk.Button("Show graph")
		self.showgraphbutton.show()
		self.vbox.pack_start(self.showgraphbutton, True, True, 0)

	def addExportGraphButton(self):
		self.exportgraphbutton = gtk.Button("Export graph")
		self.exportgraphbutton.show()
		self.vbox.pack_start(self.exportgraphbutton, True, True, 0)

	def addListOfNodesButton(self):
		self.listofnodesbutton = gtk.Button("Get list of nodes")
		self.listofnodesbutton.show()
		self.vbox.pack_start(self.listofnodesbutton, True, True, 0)

def main():
	guw = GuiOptionsWindow()
	gtk.main()

if __name__ == '__main__':
	main()

