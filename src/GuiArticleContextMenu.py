# -------------------------------------------------------------------------------
# Name:        GuiArticleContextMenu
# Purpose:     Article context menu for the citation mapper program
#
# Author:      Henrik Skov Midtiby
#
# Created:     2011-02-25
# Copyright:   (c) Henrik Skov Midtiby 2011
# Licence:     <your licence>
# -------------------------------------------------------------------------------
#!/usr/bin/env python

import gi
gi.require_version("Gtk", "3.0")
from gi.repository import Gtk as gtk


class GuiArticleContextMenu:
    def __init__(self, directoryName):
        self.opendirectory = directoryName

    def add_to_ban_list(self, widget, data=None):
        print("AddingToBanList dir: %s  item: %s" % (self.opendirectory, data))
        filename = "%s/banlist" % self.opendirectory
        try:
            filehandle = open(filename, "a")
            filehandle.write("%s\n" % data)
            filehandle.close()
        except IOError:
            pass
        return False

    def hello(self, widget, data=None):
        print("hello")
        print(data)
        return False

    def show_context_menu(self, widget, data, event):
        menu = gtk.Menu()
        one = gtk.MenuItem("Add to ban list")
        one.connect("activate", self.add_to_ban_list, data)
        menu.append(one)
        menu.show_all()
        menu.popup(None, None, None, event.button, event.get_time())
        return True
