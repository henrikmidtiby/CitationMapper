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

	def __init__(self):
		searchoptionswindow = gtk.Window()
		searchoptionswindow.set_border_width(10)
		vbox = gtk.VBox(False, 0)
		searchoptionswindow.add(vbox)
		self.adjMinNumberOfReferences = gtk.Adjustment(value=self.minNumberOfReferences, lower=0, upper=50, step_incr=1, page_incr=5, page_size=0)
		hscrollbarReferences = gtk.HScale(self.adjMinNumberOfReferences)
		hscrollbarReferences.set_digits(0)
		hscrollbarReferences.set_value_pos(gtk.POS_LEFT)
		self.adjMinNumberOfCitations = gtk.Adjustment(value=self.minNumberOfCitations, lower=0, upper=50, step_incr=1, page_incr=5, page_size=0)
		hscrollbarCitations = gtk.HScale(self.adjMinNumberOfCitations)
		hscrollbarCitations.set_digits(0)
		hscrollbarCitations.set_value_pos(gtk.POS_LEFT)
		self.showgraphbutton = gtk.Button("Show graph")
		self.exportgraphbutton = gtk.Button("Export graph")
		self.listofnodesbutton = gtk.Button("Get list of nodes")
		labelReferences = gtk.Label("Number of references")
		labelCitations = gtk.Label("Number of citations")
		self.labelGraphSize = gtk.Label("Graph size: nodes / edges")
		self.showgraphbutton.show()
		self.exportgraphbutton.show()
		self.listofnodesbutton.show()
		labelReferences.show()
		labelCitations.show()
		self.labelGraphSize.show()
		hscrollbarReferences.show()
		hscrollbarCitations.show()
		vbox.pack_start(labelReferences, True, True, 0)
		vbox.pack_start(hscrollbarReferences, True, True, 0)
		vbox.pack_start(labelCitations, True, True, 0)
		vbox.pack_start(hscrollbarCitations, True, True, 0)
		vbox.pack_start(self.labelGraphSize, True, True, 0)
		vbox.pack_start(self.showgraphbutton, True, True, 0)
		vbox.pack_start(self.exportgraphbutton, True, True, 0)
		vbox.pack_start(self.listofnodesbutton, True, True, 0)
		vbox.show()
		searchoptionswindow.show()

def main():
	guw = GuiOptionsWindow()
	gtk.main()

if __name__ == '__main__':
	main()

