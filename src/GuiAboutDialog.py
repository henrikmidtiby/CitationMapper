#-------------------------------------------------------------------------------
# Name:        GuiAboutDialog
# Purpose:     About dialog for the citation mapper program
#
# Author:      Henrik Skov Midtiby
#
# Created:     2011-03-07
# Copyright:   (c) Henrik Skov Midtiby 2011
# Licence:     <your licence>
#-------------------------------------------------------------------------------
#!/usr/bin/env python

import gtk

class GuiAboutDialog:
	def __init__(self):
		self.aboutdialog = None
		self.vbox = None
		self.label = None
		self.label2 = None
		self.closebotton = None
		self.setupCanvas()
		self.addLabel()
		self.addLabel2()
		self.addCloseButton()
		self.aboutdialog.add(self.vbox)
		self.aboutdialog.show_all()

	def setupCanvas(self):
		self.aboutdialog = gtk.Window(gtk.WINDOW_TOPLEVEL)
		self.aboutdialog.set_title("About dialog")
		self.aboutdialog.set_border_width(10)
		self.vbox = gtk.VBox(False, 0)

	def addLabel(self):
		self.label = gtk.Label("Citation mapper was developed by "
			+ "Henrik Skov Midtiby (hemi@kbm.sdu.dk), University of Southern Denmark. ")
		self.label.set_line_wrap(True)
		self.label.show()
		self.vbox.pack_start(self.label, True, True, 5)

	def addLabel2(self):
		self.label2 = gtk.Label("Version 2011-08-03")
		self.label2.set_line_wrap(True)
		self.label2.set_alignment(0, 0)
		self.label2.show()
		self.vbox.pack_start(self.label2, True, True, 5)

	def addCloseButton(self):
		self.closebotton = gtk.Button("Close")
		self.closebotton.show()
		self.vbox.pack_start(self.closebotton, True, False, 5)
		self.closebotton.connect("clicked", self.closeAction, None)

	def closeAction(self, action, data):
		self.aboutdialog.destroy()

def main():
	gab = GuiAboutDialog()
	gab.aboutdialog.connect('destroy', gtk.main_quit)
	gtk.main()

if __name__ == '__main__':
	main()
