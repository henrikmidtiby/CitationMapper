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

import gtk


class GuiOptionsWindow:
    min_number_of_references = 1
    min_number_of_citations = 3
    min_number_of_references_two = 1
    min_number_of_citations_two = 3
    graph_size = 0

    def __init__(self, maxCitations=50, maxReferences=50):
        self.ignoreArticlesButton = None
        self.hscrollbarCitations = None
        self.hscrollbarReferences = None
        self.adjMinNumberOfCitations = None
        self.adjMinNumberOfReferences = None
        self.adjMinNumberOfCitationsTwo = None
        self.adjMinNumberOfReferencesTwo = None
        self.exportgraphbutton = None
        self.labelGraphSize = None
        self.listofnodesbutton = None
        self.showgraphbutton = None

        self.searchoptionswindow = gtk.Window()
        self.searchoptionswindow.set_border_width(10)
        self.vbox = gtk.VBox(False, 0)
        self.searchoptionswindow.add(self.vbox)
        self.add_label_references()
        self.add_hscrollbar_references(maxReferences)
        self.add_label_citations()
        self.add_hscrollbar_citations(maxCitations)
        self.add_label_references_two()
        self.add_hscrollbar_references_two(maxReferences)
        self.add_label_citations_two()
        self.add_hscrollbar_citations_two(maxCitations)
        self.add_label_graph_size()
        self.add_show_graph_button()
        self.add_export_graph_button()
        self.add_list_of_nodes_button()
        self.add_ignore_articles_button()
        self.vbox.show()
        self.searchoptionswindow.show()

    def add_label_references(self):
        labelReferences = gtk.Label("Number of references")
        labelReferences.show()
        self.vbox.pack_start(labelReferences, True, True, 0)

    def add_hscrollbar_references(self, maxReferences):
        self.adjMinNumberOfReferences = gtk.Adjustment(
            value=self.min_number_of_references,
            lower=0,
            upper=maxReferences,
            step_incr=1,
            page_incr=5,
            page_size=0)
        self.hscrollbarReferences = gtk.HScale(self.adjMinNumberOfReferences)
        self.hscrollbarReferences.set_digits(0)
        self.hscrollbarReferences.set_value_pos(gtk.POS_LEFT)
        self.hscrollbarReferences.show()
        self.vbox.pack_start(self.hscrollbarReferences, True, True, 0)

    def add_label_citations(self):
        labelCitations = gtk.Label("Number of citations")
        labelCitations.show()
        self.vbox.pack_start(labelCitations, True, True, 0)

    def add_hscrollbar_citations(self, maxCitations):
        self.adjMinNumberOfCitations = gtk.Adjustment(
            value=self.min_number_of_citations,
            lower=0,
            upper=maxCitations,
            step_incr=1,
            page_incr=5,
            page_size=0)
        self.hscrollbarCitations = gtk.HScale(self.adjMinNumberOfCitations)
        self.hscrollbarCitations.set_digits(0)
        self.hscrollbarCitations.set_value_pos(gtk.POS_LEFT)
        self.hscrollbarCitations.show()
        self.vbox.pack_start(self.hscrollbarCitations, True, True, 0)

    def add_label_references_two(self):
        labelReferences = gtk.Label("Number of references")
        labelReferences.show()
        self.vbox.pack_start(labelReferences, True, True, 0)

    def add_hscrollbar_references_two(self, maxReferences):
        self.adjMinNumberOfReferencesTwo = gtk.Adjustment(
            value=self.min_number_of_references_two,
            lower=0,
            upper=maxReferences,
            step_incr=1,
            page_incr=5,
            page_size=0)
        self.hscrollbar_references_two = gtk.HScale(
            self.adjMinNumberOfReferencesTwo)
        self.hscrollbar_references_two.set_digits(0)
        self.hscrollbar_references_two.set_value_pos(gtk.POS_LEFT)
        self.hscrollbar_references_two.show()
        self.vbox.pack_start(self.hscrollbar_references_two, True, True, 0)

    def add_label_citations_two(self):
        label_citations = gtk.Label("Number of citations")
        label_citations.show()
        self.vbox.pack_start(label_citations, True, True, 0)

    def add_hscrollbar_citations_two(self, maxCitations):
        self.adjMinNumberOfCitationsTwo = gtk.Adjustment(
            value=self.min_number_of_citations_two,
            lower=0,
            upper=maxCitations,
            step_incr=1,
            page_incr=5,
            page_size=0)
        self.hscrollbarCitationsTwo = gtk.HScale(
            self.adjMinNumberOfCitationsTwo)
        self.hscrollbarCitationsTwo.set_digits(0)
        self.hscrollbarCitationsTwo.set_value_pos(gtk.POS_LEFT)
        self.hscrollbarCitationsTwo.show()
        self.vbox.pack_start(self.hscrollbarCitationsTwo, True, True, 0)

    def add_label_graph_size(self):
        self.labelGraphSize = gtk.Label("Graph size: nodes")
        self.labelGraphSize.show()
        self.vbox.pack_start(self.labelGraphSize, True, True, 0)

    def add_show_graph_button(self):
        self.showgraphbutton = gtk.Button("Show graph")
        self.showgraphbutton.show()
        self.vbox.pack_start(self.showgraphbutton, True, True, 0)

    def add_export_graph_button(self):
        self.exportgraphbutton = gtk.Button("Export graph")
        self.exportgraphbutton.show()
        self.vbox.pack_start(self.exportgraphbutton, True, True, 0)

    def add_list_of_nodes_button(self):
        self.listofnodesbutton = gtk.Button("Get list of nodes")
        self.listofnodesbutton.show()
        self.vbox.pack_start(self.listofnodesbutton, True, True, 0)

    def add_ignore_articles_button(self):
        self.ignoreArticlesButton = gtk.Button("Ignore articles in ban file")
        self.ignoreArticlesButton.show()
        self.vbox.pack_start(self.ignoreArticlesButton, True, True, 0)


def main():
    GuiOptionsWindow()
    gtk.main()


if __name__ == '__main__':
    main()
