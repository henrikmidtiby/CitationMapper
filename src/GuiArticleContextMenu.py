#-------------------------------------------------------------------------------
# Name:        GuiArticleContextMenu
# Purpose:     Article context menu for the citation mapper program
#
# Author:      Henrik Skov Midtiby
#
# Created:     2011-02-25
# Copyright:   (c) Henrik Skov Midtiby 2011
# Licence:     <your licence>
#-------------------------------------------------------------------------------
#!/usr/bin/env python

import gtk


class GuiArticleContextMenu:
    def __init__(self, directoryName):
        self.opendirectory = directoryName

    def addToBanList(self, widget, data=None):
        print "AddingToBanList dir: %s  item: %s" % (self.opendirectory, data)
        filename = "%s/banlist" % self.opendirectory
        try:
            filehandle = open(filename, 'a')
            filehandle.write("%s\n" % data)
        except (IOError):
            pass
        filehandle.close()
        return False

    def hello(self, widget, data=None):
        print "hello"
        print data
        return False

    def showContextMenuOld(self, widget, data, event):
        menu = gtk.Menu()
        one = gtk.MenuItem("One")
        menu.append(one)
        submenu = gtk.Menu()
        two = gtk.MenuItem("Two")
        two.connect("activate", self.hello)
        submenu.append(two)
        one.set_submenu(submenu)
        three = gtk.MenuItem("Three")
        three.connect("activate", self.hello)
        menu.append(three)
        menu.show_all()
        menu.popup(None, None, None, event.button, event.get_time())
        return True

    def showContextMenu(self, widget, data, event):
        menu = gtk.Menu()
        one = gtk.MenuItem("Add to ban list")
        one.connect("activate", self.addToBanList, data)
        menu.append(one)
        menu.show_all()
        menu.popup(None, None, None, event.button, event.get_time())
        return True
