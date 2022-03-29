#-------------------------------------------------------------------------------
# Name:        GuiMainWindow
# Purpose:     Main window for the citation mapper program
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

import os
import gi
gi.require_version('Gtk', '3.0')
from gi.repository import Gtk
import io
import sys
import string

import xdot
import citationmapbuilder

import GuiArticleDetailsWindowHandler
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
                <menuitem action="OpenOptionsDialog"/>
                <menuitem action="CloseArticleDetailsWindows"/>
                <menuitem action="Print"/>
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
            <toolitem action="Print"/>
        </toolbar>
    </ui>
    '''

    openfilename = None

    def __init__(self):
        self.orig_network_pre_filtered = None
        self.orig_network = None
        self.options_window = None
        self.actiongroup = None
        self.max_references = None
        self.article_details_window = None
        self.quit_dialog = None
        self.citationmapper_window = None
        self.orig_network_citations = None
        self.orig_network_references = None
        self.included_node_names = []
        self.excluded_node_names = []
        self.max_citations = None
        self.uimanager = None
        self.mapview = None
        self.article_details_windows = \
            GuiArticleDetailsWindowHandler.GuiArticleDetailsWindowHandler()
        self.setup_window_contents()
        self.setup_connections()
        self.citationmap = citationmapbuilder.citationmapbuilder()

    def setup_window_contents(self):
        self.citationmapper_window = Gtk.Window()
        self.citationmapper_window.set_title("Citation mapper")
        self.citationmapper_window.set_size_request(500, 200)

        # Create a UIManager instance
        uimanager = self.uimanager = Gtk.UIManager()

        # Outer vertical box
        vbox = Gtk.VBox(False, 0)

        # Network window
        self.mapview = xdot.DotWidget()

        # Action bar
        # Create an ActionGroup
        actiongroup = Gtk.ActionGroup('Actions')
        self.actiongroup = actiongroup

        # Create actions
        actiongroup.add_actions((
            ('Open', Gtk.STOCK_OPEN, None, None, None, self.on_open),
            ('Reload', Gtk.STOCK_REFRESH, None, None, None, self.on_reload),
            ('ZoomIn', Gtk.STOCK_ZOOM_IN, None, None, None, self.mapview.on_zoom_in),
            ('ZoomOut', Gtk.STOCK_ZOOM_OUT, None, None, None, self.mapview.on_zoom_out),
            ('ZoomFit', Gtk.STOCK_ZOOM_FIT, None, None, None, self.mapview.on_zoom_fit),
            ('Zoom100', Gtk.STOCK_ZOOM_100, None, None, None, self.mapview.on_zoom_100),
            ('Print', Gtk.STOCK_PRINT, None, None, None, self.mapview.on_print),
        ))


        actiongroup.add_actions([
            ('Quit', Gtk.STOCK_QUIT, '_Quit', None, None, Gtk.main_quit),
            ('CloseArticleDetailsWindows', None, '_Close all article details windows', 'C',
                    None, self.article_details_windows.close_all),
            ('OpenOptionsDialog', None, '_Options', 'O', None, self.show_options_window),
            ('Print', None, '_Export to pdf', 'E', None, self.mapview.on_print),
            ('About', None, '_About', None, None, self.show_about_dialog),
            ('File', None, '_File'),
            ('Help', None, '_Help')])

        # Add the actiongroup to the uimanager
        uimanager.insert_action_group(actiongroup, 0)

        # Add the accelerator group to the toplevel window
        accelgroup = uimanager.get_accel_group()
        self.citationmapper_window.add_accel_group(accelgroup)

        # Add a UI descrption
        uimanager.add_ui_from_string(self.ui)

        # Create a menu
        menuline = uimanager.get_widget('/MenuBar')
        vbox.pack_start(menuline, False, False, 0)

        # Create a Toolbar
        toolbar = uimanager.get_widget('/ToolBar')
        vbox.pack_start(toolbar, False, False, 0)
        #vbox.pack_start(labelReferences, False, True, 0)
        vbox.pack_start(self.mapview, True, True, 0)

        vbox.show_all()
        self.citationmapper_window.add(vbox)
        self.citationmapper_window.show()

        print(type(self.dotcode))
        print(repr(self.dotcode))
        self.mapview.set_dotcode(bytes(self.dotcode, encoding='UTF-8'))

    def change_color_of_node(self, url, newcolor):
        temp = self.mapview.graph
        for node in temp.nodes:
            if isinstance(node, xdot.ui.elements.Node) and node.url == url:
                for shape in node.shapes:
                    if isinstance(shape, xdot.ui.elements.TextShape):
                        print(shape.t)
                    if isinstance(shape, xdot.ui.elements.EllipseShape):
                        shape.pen.fillcolor = newcolor
                        shape.pen.color = newcolor
        self.mapview.queue_draw()

    def setup_connections(self):
        self.mapview.connect('clicked', self.article_clicked)
        self.citationmapper_window.connect('destroy', Gtk.main_quit)

    def article_clicked(self, widget, data, event):
        if event.button == 1:
            self.article_details_windows.open_new_article_details_window(data)
            self.change_color_of_node(data, (1, 0.75, 0.75, 1))
        else:
            article_context_menu = GuiArticleContextMenu.GuiArticleContextMenu(
                self.openfilename)
            article_context_menu.show_context_menu(widget, data, event)

    def calculate_new_graph_size_and_update_options_window(self, placeholder=None):
        # Count the number of articles with the required number of references and citations.
        number_of_matching_nodes = 0
        self.included_node_names = []
        self.excluded_node_names = []
        for key in self.orig_network.nodes():
            number_of_citations = self.orig_network.out_degree(key)
            number_of_references = self.orig_network.in_degree(key)
            test_one = (
                number_of_citations >= self.options_window.min_number_of_citations and
                number_of_references >= self.options_window.min_number_of_references)
            test_two = (
                number_of_citations >= self.options_window.min_number_of_citations_two
                and number_of_references >= self.options_window.min_number_of_references_two)
            test_three = False
            try:
                if self.citationmap.articles[key].year > self.options_window.min_year:
                    test_three = True
            except KeyError:
                pass
            if (test_one or test_two) and test_three:
                number_of_matching_nodes += 1
                self.included_node_names.append(key)
            else:
                self.excluded_node_names.append(key)

        self.citationmap.remove_named_nodes(self.excluded_node_names)
        self.options_window.set_graph_size(number_of_matching_nodes)

    def show_options_window(self, action=None):
        try:
            self.options_window.searchoptions_window.destroy()
        except:
            pass

        self.options_window = GuiOptionsWindow.GuiOptionsWindow(self.max_citations, self.max_references)
        self.options_window.connect("show_graph_activated", self.filter_and_show_current_citation_map, None)
        self.options_window.connect("export_graph_activated", self.export_filtered_citation_map, None)
        self.options_window.connect("show_list_of_nodes", self.get_list_of_nodes, None)
        self.options_window.connect("ignore_articles_activated", self.ignore_articles_in_ban_file, None)
        self.calculate_new_graph_size_and_update_options_window()

        self.options_window.connect("search_parameters_changed", self.calculate_new_graph_size_and_update_options_window)

    def on_open(self, action):
        chooser = Gtk.FileChooserDialog(
            title="Open directory with bibliography",
            action=Gtk.FileChooserAction.SELECT_FOLDER,
            buttons=(Gtk.STOCK_CANCEL, Gtk.ResponseType.CANCEL, Gtk.STOCK_OPEN,
                     Gtk.ResponseType.OK))
        chooser.set_default_response(Gtk.ResponseType.OK)
        if chooser.run() == Gtk.ResponseType.OK:
            filename = chooser.get_filename()
            chooser.destroy()
            self.open_directory(filename)
            self.show_options_window()
        else:
            chooser.destroy()

    def on_reload(self, action):
        if self.openfilename is not None:
            try:
                self.open_directory(self.openfilename)
                self.show_options_window()
            except IOError:
                pass

    def open_directory(self, directory):
        self.openfilename = directory
        self.citationmap.__init__()
        files = os.listdir(directory)
        print("<open_directory>")
        for current_file in files:
            full_path_name = os.path.join(directory, current_file)
            if os.path.isfile(full_path_name):
                print("Parsing file: %s" % current_file)
                self.citationmap.parse_file(full_path_name)
                print("</open_directory>")
        self.update_orig_network()

    def update_orig_network(self):
        self.orig_network_pre_filtered = self.citationmap.graph.copy()
        self.orig_network = self.orig_network_pre_filtered.copy()
        self.calculate_network_properties()

    def calculate_network_properties(self):
        self.orig_network_citations = self.orig_network.out_degree()
        self.orig_network_references = self.orig_network.in_degree()
        assert (len(self.orig_network_citations) ==
                len(self.orig_network_references))
        try:
            self.max_citations = max(self.orig_network_citations.values())
            self.max_references = max(self.orig_network_references.values())
        except:
            self.max_citations = 20
            self.max_references = 20

    def filter_current_citation_map(self):
        self.citationmap.graph = self.orig_network.copy()
        self.citationmap.analyze_graph()
        self.citationmap.remove_named_nodes(self.excluded_node_names)

    def filter_and_export_current_citation_map(self):
        self.filter_current_citation_map()
        output = io.StringIO()
        self.citationmap.output_graph(output, "BT")
        dotcode = output.getvalue()
        return dotcode

    def filter_and_show_current_citation_map(self, action, data):
        if self.options_window.graph_size > 200:
            if not self.dialog_show_large_graph(self.options_window.graph_size):
                return
        dotcode = self.filter_and_export_current_citation_map()
        self.mapview.set_dotcode(bytes(dotcode, encoding='UTF-8'))
        self.mapview.zoom_to_fit()
        self.article_details_windows.set_citationmap(self.citationmap)

    def dialog_show_large_graph(self, nNodes):
        self.quit_dialog = Gtk.Dialog()

        # Set it modal and transient for main window.
        self.quit_dialog.set_modal(True)
        #self.quit_dialog.set_transient_for( self )

        # Set title
        self.quit_dialog.set_title('Confirmation')

        # Add buttons.
        self.quit_dialog.add_button(Gtk.STOCK_YES, 1)
        self.quit_dialog.add_button(Gtk.STOCK_NO, 2)

        # Create label
        label = Gtk.Label(
            'Will you really visualize this huge graph? (# nodes = %d)' %
            nNodes)

        self.quit_dialog.vbox.pack_start(label, False, False, 0)

        # Show dialog
        self.quit_dialog.show_all()

        # Run dialog
        response = self.quit_dialog.run()
        self.quit_dialog.hide()

        return response == 1

    def export_filtered_citation_map(self, action, data):
        dialog = Gtk.MessageDialog(self.citationmapper_window, 0, Gtk.MessageType.INFO,
                Gtk.ButtonsType.OK, "Guide for exporting the graph")
        dialog.format_secondary_text(
            "Choose a place for the .dot file that will be generated. Afterwards the dot command from graphviz can be used to convert the .dot file to a pdf.")
        dialog.run()
        dialog.destroy()
        chooser = Gtk.FileChooserDialog(
            title=None,
            action=Gtk.FileChooserAction.SAVE,
            buttons=(Gtk.STOCK_CANCEL, Gtk.ResponseType.CANCEL, Gtk.STOCK_SAVE,
                     Gtk.ResponseType.OK))
        if chooser.run() == Gtk.ResponseType.OK:
            filename = chooser.get_filename()
            chooser.destroy()

            exportfile = open(filename, 'w')
            dotcode = self.filter_and_export_current_citation_map()
            exportfile.write(dotcode)
            exportfile.close()

        else:
            chooser.destroy()
        return False

    def handle_click_in_list_of_nodes(self, v1, article_id, v3):
        self.article_details_windows.open_new_article_details_window(article_id)

    def get_list_of_nodes(self, action, data):
        list_of_nodes = GuiListOfArticlesInGraph.GuiListOfArticlesInGraph()
        self.filter_current_citation_map()
        list_of_nodes.nodesTreestore.clear()
        list_of_nodes.connect("citation_clicked", self.handle_click_in_list_of_nodes, None)
        for key in self.citationmap.graphForAnalysis.nodes():
            try:
                network_citations = self.orig_network.out_degree(key)
                network_references = self.orig_network.in_degree(key)
                article = self.citationmap.articles[key]
                article.retrieve_information_based_on_doi()
                year = article.year
                fieldSO = article.journal
                if type(fieldSO) is list:
                    fieldSO = "".join(fieldSO)
                fieldTitle = article.title
                if type(fieldTitle) is list:
                    fieldTitle = "".join(article.title)
                fieldAuthors = " and ".join(article.authors)
                fieldTC = 0 #int(article['TC'][0])
                fieldNR = 0 #int(article['NR'][0])
                list_of_nodes.nodesTreestore.append(None,
                                                  [key, year, network_citations,
                                                   network_references, fieldTC,
                                                   fieldNR, fieldSO,
                                                   fieldAuthors, fieldTitle])
            except KeyError:
                list_of_nodes.nodesTreestore.append(None,
                                                  [key, -1, network_citations,
                                                   network_references, -1, -1,
                                                   "", "", ""])

    def ignore_articles_in_ban_file(self, action, data):
        self.orig_network = self.orig_network_pre_filtered.copy()
        filename = "%s/banlist" % self.openfilename
        try:
            file_handle = open(filename)
            for line in file_handle:
                article_identifier = line[:-1]
                try:
                    # Remove things that are only mentioned by the node
                    things_referenced = self.orig_network.in_edges(
                        [article_identifier])
                    for edge in things_referenced:
                        referenced_article = edge[0]
                        number_of_citations = self.orig_network.out_degree(
                            referenced_article)
                        if number_of_citations == 1:
                            print( referenced_article)
                            self.orig_network.remove_node(referenced_article)

                    # Remove node
                    print(article_identifier)
                    self.orig_network.remove_node(article_identifier)
                except IOError:
                    pass
                except:
                    print("Unknown error detected")

        except IOError:
            pass
        self.calculate_network_properties()
        self.show_options_window()

    def show_about_dialog(self, action):
        GuiAboutDialog.GuiAboutDialog()


def main():
    gmw = GuiMainWindow()

    if len(sys.argv) > 1:
        gmw.open_directory(sys.argv[1])
        gmw.show_options_window()

    Gtk.main()


if __name__ == '__main__':
    main()
