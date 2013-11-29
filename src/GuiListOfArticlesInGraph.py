#-------------------------------------------------------------------------------
# Name:        GuiListOfArticlesInGraph
# Purpose:     List of articles in graph for the citation mapper program
#
# Author:      Henrik Skov Midtiby
#
# Created:     2011-02-25
# Copyright:   (c) Henrik Skov Midtiby 2011
# Licence:     LGPL
#-------------------------------------------------------------------------------
#!/usr/bin/env python
#
# Copyright 2011 Henrik Skov Midtiby
#
# This program is free software: you can redistribute it and/or modify it
# under the terms of the GNU Lesser General Public License as published
# by the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU Lesser General Public License for more details.
#
# You should have received a copy of the GNU Lesser General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.
#

import gtk
import StringIO

class GuiListOfArticlesInGraph:
    def __init__(self):
        self.tvcolumn = None
        self.nodesTreestore = None
        self.nodesTreeview = None
        self.nodescrolledwindow = None

        self.nodewindow = gtk.Window(gtk.WINDOW_TOPLEVEL)
        self.nodewindow.set_title("List of nodes")
        self.nodewindow.set_size_request(200, 200)
        self.generateNodesTreeStore()
        self.generateNodesTreeView()
        self.generateNodeScrolledWindow()
        vbox = gtk.VBox(False, 0)
        self.nodewindow.add(vbox)
        exportlistofnodesbutton = gtk.Button("Export list of nodes")
        exportlistofnodesbutton.connect("clicked", self.exportListOfNodes, None)
        exportlistofnodesbutton.show()
        vbox.pack_start(self.nodescrolledwindow, True, True, 0)
        vbox.pack_start(exportlistofnodesbutton, False, False, 0)
        self.nodescrolledwindow.show_all()
        self.nodewindow.show_all()

    def generateNodesTreeStore(self):
        # create a TreeStore with one string column to use as the model
        self.nodesTreestore = gtk.TreeStore(str, int, int, int, int, int, str, str, str)


    def generateNodesTreeView(self):
        tmsort = gtk.TreeModelSort(self.nodesTreestore) # produce a sortable treemodel
        self.nodesTreeview = gtk.TreeView(tmsort)
        self.nodesTreeview.connect("row-activated", self.row_clicked)

        column_names = ['ID', 'Year', 'In graph citations', 'In graph references', 'Total citations', 'Total references', 'Journal', 'Authors', 'Title']

        self.tvcolumn = [None] * len(column_names)
        for n in range(0, len(column_names)):
            cell = gtk.CellRendererText()
            self.tvcolumn[n] = gtk.TreeViewColumn(column_names[n])
            self.tvcolumn[n].pack_start(cell, True)
            self.tvcolumn[n].add_attribute(cell, 'text', n)
            self.tvcolumn[n].set_sort_column_id(n)
            self.tvcolumn[n].set_resizable(True)
            self.tvcolumn[n].set_reorderable(True)
            if n == 1:
                cell.set_property('xalign', 1.0)
            self.nodesTreeview.append_column(self.tvcolumn[n])

    def generateNodeScrolledWindow(self):
        self.nodescrolledwindow = gtk.ScrolledWindow()
        self.nodescrolledwindow.set_shadow_type(gtk.SHADOW_ETCHED_IN)
        self.nodescrolledwindow.set_policy(gtk.POLICY_AUTOMATIC, gtk.POLICY_AUTOMATIC)
        self.nodescrolledwindow.add(self.nodesTreeview)

    def row_clicked(self, widget, row, col):
        model = widget.get_model()
        text = "%s %d %d %d" % (model[row][0], model[row][1], model[row][2], model[row][3])
        print(text)

    def exportListOfNodes(self, widget, temp2 = None):
        chooser = gtk.FileChooserDialog(title=None, action=gtk.FILE_CHOOSER_ACTION_SAVE,
                        buttons=(gtk.STOCK_CANCEL, gtk.RESPONSE_CANCEL, gtk.STOCK_SAVE, gtk.RESPONSE_OK))
        if chooser.run() == gtk.RESPONSE_OK:
            filename = chooser.get_filename()
            chooser.destroy()

            exportfile = open(filename, 'w')
            htmlcode = self.encodeCurrentListAsHTML()
            exportfile.write(htmlcode)
            exportfile.close()

        else:
            chooser.destroy()
        return False


    def encodeCurrentListAsHTML(self):
        output = StringIO.StringIO()

        output.write("<html><body><table>")
        values = self.nodesTreeview.get_model()
        for row in values:
            output.write("<tr>\n")
            for elem in row:
                output.write("<td>" + str(elem) + "</td>")
            output.write("</tr>\n")
        output.write("</table>\n")
        output.write("</body>\n")
        output.write("</html>\n")

        return output.getvalue()

def main():
    loaig = GuiListOfArticlesInGraph()
    loaig.nodewindow.connect('destroy', gtk.main_quit)
    gtk.main()

if __name__ == '__main__':
    main()
