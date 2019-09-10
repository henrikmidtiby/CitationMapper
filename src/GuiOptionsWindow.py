#-------------------------------------------------------------------------------
# Name:        GuiOptionsWindow
# Purpose:     Graph showing options window for the citation mapper program
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

from gi.repository import GObject, Gtk


class GuiOptionsWindow(GObject.GObject):
    min_number_of_references = 1
    min_number_of_citations = 3
    min_number_of_references_two = 0
    min_number_of_citations_two = 20
    min_year = 1950
    graph_size = 0

    def __init__(self, maxCitations=50, maxReferences=50):
        GObject.GObject.__init__(self)
        self.ignore_articles_button = None
        self.hscrollbar_citations = None
        self.hscrollbar_references = None
        self.adj_min_number_of_citations = None
        self.adj_min_number_of_references = None
        self.adj_min_number_of_citations_two = None
        self.adj_min_number_of_references_two = None
        self.adj_min_year = None
        self.export_graph_button = None
        self.label_graph_size = None
        self.list_of_nodes_button = None
        self.show_graph_button = None

        self.searchoptions_window = Gtk.Window()
        self.searchoptions_window.set_border_width(10)
        self.vbox = Gtk.VBox(False, 0)
        self.searchoptions_window.add(self.vbox)
        self.add_label_references()
        self.add_hscrollbar_references(maxReferences)
        self.add_label_citations()
        self.add_hscrollbar_citations(maxCitations)
        self.add_label_references_two()
        self.add_hscrollbar_references_two(maxReferences)
        self.add_label_citations_two()
        self.add_hscrollbar_citations_two(maxCitations)
        self.add_hscrollbar_min_year()
        self.add_label_graph_size()
        self.add_show_graph_button()
        self.add_export_graph_button()
        self.add_list_of_nodes_button()
        self.add_ignore_articles_button()
        self.vbox.show()
        self.searchoptions_window.show()

    def add_label_references(self):
        label_references = Gtk.Label("Number of references")
        label_references.show()
        self.vbox.pack_start(label_references, True, True, 0)

    def add_hscrollbar_references(self, max_references):
        self.adj_min_number_of_references = Gtk.Adjustment(
            value=self.min_number_of_references,
            lower=0,
            upper=max_references,
            step_incr=1,
            page_incr=5,
            page_size=0)
        self.adj_min_number_of_references.connect("value_changed", self.update_min_number_of_references)
        self.hscrollbar_references = Gtk.Scale.new(Gtk.Orientation.HORIZONTAL, self.adj_min_number_of_references)
        self.hscrollbar_references.set_digits(0)
        #self.hscrollbar_references.set_value_pos(Gtk.POS_LEFT)
        self.hscrollbar_references.show()
        self.vbox.pack_start(self.hscrollbar_references, True, True, 0)

    def add_label_citations(self):
        label_citations = Gtk.Label("Number of citations")
        label_citations.show()
        self.vbox.pack_start(label_citations, True, True, 0)

    def add_hscrollbar_citations(self, max_citations):
        self.adj_min_number_of_citations = Gtk.Adjustment(
            value=self.min_number_of_citations,
            lower=0,
            upper=max_citations,
            step_incr=1,
            page_incr=5,
            page_size=0)
        self.adj_min_number_of_citations.connect("value_changed", self.update_min_number_of_citations)
        self.hscrollbar_citations = Gtk.Scale.new(Gtk.Orientation.HORIZONTAL, self.adj_min_number_of_citations)
        self.hscrollbar_citations.set_digits(0)
        #self.hscrollbar_citations.set_value_pos(Gtk.POS_LEFT)
        self.hscrollbar_citations.show()
        self.vbox.pack_start(self.hscrollbar_citations, True, True, 0)

    def add_label_references_two(self):
        label_references = Gtk.Label("Number of references")
        label_references.show()
        self.vbox.pack_start(label_references, True, True, 0)

    def add_hscrollbar_references_two(self, max_references):
        self.adj_min_number_of_references_two = Gtk.Adjustment(
            value=self.min_number_of_references_two,
            lower=0,
            upper=max_references,
            step_incr=1,
            page_incr=5,
            page_size=0)
        self.adj_min_number_of_references_two.connect("value_changed", self.update_min_number_of_references_two)
        self.hscrollbar_references_two = Gtk.Scale.new(
            Gtk.Orientation.HORIZONTAL,
            self.adj_min_number_of_references_two)
        self.hscrollbar_references_two.set_digits(0)
        #self.hscrollbar_references_two.set_value_pos(Gtk.POS_LEFT)
        self.hscrollbar_references_two.show()
        self.vbox.pack_start(self.hscrollbar_references_two, True, True, 0)

    def add_label_citations_two(self):
        label_citations = Gtk.Label("Number of citations")
        label_citations.show()
        self.vbox.pack_start(label_citations, True, True, 0)

    def add_hscrollbar_citations_two(self, maxCitations):
        self.adj_min_number_of_citations_two = Gtk.Adjustment(
            value=self.min_number_of_citations_two,
            lower=0,
            upper=maxCitations,
            step_incr=1,
            page_incr=5,
            page_size=0)
        self.adj_min_number_of_citations_two.connect("value_changed", self.update_min_number_of_citations_two)
        self.hscrollbar_citations_two = Gtk.Scale.new(
            Gtk.Orientation.HORIZONTAL, 
            self.adj_min_number_of_citations_two)
        self.hscrollbar_citations_two.set_digits(0)
        #self.hscrollbar_citations_two.set_value_pos(Gtk.POS_LEFT)
        self.hscrollbar_citations_two.show()
        self.vbox.pack_start(self.hscrollbar_citations_two, True, True, 0)

    def add_hscrollbar_min_year(self):
        self.adj_min_year = Gtk.Adjustment(
            value=self.min_year,
            lower=1900,
            upper=2020,
            step_incr=1,
            page_incr=5,
            page_size=0)
        self.adj_min_year.connect("value_changed", self.update_min_year)
        self.hscrollbar_min_year = Gtk.Scale.new(
            Gtk.Orientation.HORIZONTAL,
            self.adj_min_year)
        self.hscrollbar_min_year.set_digits(0)
        #self.hscrollbar_min_year.set_value_pos(Gtk.POS_LEFT)
        self.hscrollbar_min_year.show()
        self.vbox.pack_start(self.hscrollbar_min_year, True, True, 0)

    def add_label_graph_size(self):
        self.label_graph_size = Gtk.Label("Graph size: nodes")
        self.label_graph_size.show()
        self.vbox.pack_start(self.label_graph_size, True, True, 0)

    def add_show_graph_button(self):
        self.show_graph_button = Gtk.Button("Show graph")
        self.show_graph_button.show()
        self.vbox.pack_start(self.show_graph_button, True, True, 0)
        self.show_graph_button.connect("clicked", lambda self, x: x.emit('show_graph_activated'), self)

    def add_export_graph_button(self):
        self.export_graph_button = Gtk.Button("Export graph")
        self.export_graph_button.show()
        self.vbox.pack_start(self.export_graph_button, True, True, 0)
        self.export_graph_button.connect("clicked", lambda self, x: x.emit('export_graph_activated'), self)

    def add_list_of_nodes_button(self):
        self.list_of_nodes_button = Gtk.Button("Get list of nodes")
        self.list_of_nodes_button.show()
        self.vbox.pack_start(self.list_of_nodes_button, True, True, 0)
        self.list_of_nodes_button.connect("clicked", lambda self, x: x.emit('show_list_of_nodes'), self)

    def add_ignore_articles_button(self):
        self.ignore_articles_button = Gtk.Button("Ignore articles in ban file")
        self.ignore_articles_button.show()
        self.vbox.pack_start(self.ignore_articles_button, True, True, 0)
        self.ignore_articles_button.connect("clicked", lambda self, x: x.emit('ignore_articles_activated'), self)

    def update_min_number_of_references(self, adj):
        print(adj)
        self.min_number_of_references = adj.get_value()
        self.emit('search_parameters_changed')

    def update_min_number_of_citations(self, adj):
        self.min_number_of_citations = adj.get_value()
        self.emit('search_parameters_changed')

    def update_min_number_of_references_two(self, adj):
        self.min_number_of_references_two = adj.get_value()
        self.emit('search_parameters_changed')

    def update_min_number_of_citations_two(self, adj):
        self.min_number_of_citations_two = adj.get_value()
        self.emit('search_parameters_changed')

    def update_min_year(self, adj):
        self.min_year = adj.get_value()
        self.emit('search_parameters_changed')

    def set_graph_size(self, new_graph_size):
        self.graph_size = new_graph_size
        self.label_graph_size.set_text("Graph size: %d" % new_graph_size)


GObject.type_register(GuiOptionsWindow)
GObject.signal_new("search_parameters_changed", GuiOptionsWindow, GObject.SIGNAL_RUN_FIRST,
                   GObject.TYPE_NONE, ())
GObject.signal_new("show_graph_activated", GuiOptionsWindow, GObject.SIGNAL_RUN_FIRST,
                   GObject.TYPE_NONE, ())
GObject.signal_new("export_graph_activated", GuiOptionsWindow, GObject.SIGNAL_RUN_FIRST,
                   GObject.TYPE_NONE, ())
GObject.signal_new("show_list_of_nodes", GuiOptionsWindow, GObject.SIGNAL_RUN_FIRST,
                   GObject.TYPE_NONE, ())
GObject.signal_new("ignore_articles_activated", GuiOptionsWindow, GObject.SIGNAL_RUN_FIRST,
                   GObject.TYPE_NONE, ())


def main():
    GuiOptionsWindow()
    Gtk.main()


if __name__ == '__main__':
    main()
