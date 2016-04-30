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
import gtk
import StringIO
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
    minNumberOfReferences = 1
    minNumberOfCitations = 3
    min_mumber_of_references_two = 1
    minNumberOfCitationsTwo = 3

    def __init__(self):
        self.origNetworkPreFiltered = None
        self.origNetwork = None
        self.optionsWindow = None
        self.actiongroup = None
        self.maxReferences = None
        self.articleDetailsWindow = None
        self.quit_dialog = None
        self.citationmapperwindow = None
        self.origNetworkCitations = None
        self.origNetworkReferences = None
        self.includedNodeNames = []
        self.excludedNodeNames = []
        self.maxCitations = None
        self.uimanager = None
        self.mapview = None
        self.articleDetailsWindows = \
            GuiArticleDetailsWindowHandler.GuiArticleDetailsWindowHandler()
        self.setup_window_contents()
        self.setup_connections()
        self.citationmap = citationmapbuilder.citationmapbuilder()

    def setup_window_contents(self):
        self.citationmapperwindow = gtk.Window()
        self.citationmapperwindow.set_title("Citation mapper")
        self.citationmapperwindow.set_size_request(500, 200)

        # Create a UIManager instance
        uimanager = self.uimanager = gtk.UIManager()

        # Outer vertical box
        vbox = gtk.VBox(False, 0)

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
            ('Print', gtk.STOCK_PRINT, None, None, None, self.mapview.on_print),
        ))


        actiongroup.add_actions([
            ('Quit', gtk.STOCK_QUIT, '_Quit', None, None, gtk.main_quit),
            ('CloseArticleDetailsWindows', None, '_Close all article details windows', 'C',
                    None, self.articleDetailsWindows.closeAll),
            ('OpenOptionsDialog', None, '_Options', 'O', None, self.show_options_window),
            ('Print', None, '_Export to pdf', 'E', None, self.mapview.on_print),
            ('About', None, '_About', None, None, self.show_about_dialog),
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

    def change_color_of_node(self, url, newcolor):
        temp = self.mapview.graph
        for node in temp.nodes:
            if isinstance(node, xdot.Node) and node.url == url:
                for shape in node.shapes:
                    if isinstance(shape, xdot.TextShape):
                        print shape.t
                    if isinstance(shape, xdot.EllipseShape):
                        shape.pen.fillcolor = newcolor
                        shape.pen.color = newcolor
        self.mapview.queue_draw()

    def setup_connections(self):
        self.mapview.connect('clicked', self.article_clicked)
        self.citationmapperwindow.connect('destroy', gtk.main_quit)

    def article_clicked(self, widget, data, event):
        if event.button == 1:
            self.articleDetailsWindows.openNewArticleDetailsWindow(
                data, self.citationmap)
            self.change_color_of_node(data, (1, 0.75, 0.75, 1))
        else:
            articleContextMenu = GuiArticleContextMenu.GuiArticleContextMenu(
                self.openfilename)
            articleContextMenu.show_context_menu(widget, data, event)

    def update_min_number_of_references(self, adj):
        self.minNumberOfReferences = adj.value
        self.calculate_new_graph_size_and_update_options_window()

    def update_min_number_of_citations(self, adj):
        self.minNumberOfCitations = adj.value
        self.calculate_new_graph_size_and_update_options_window()

    def update_min_number_of_references_two(self, adj):
        self.min_mumber_of_references_two = adj.value
        self.calculate_new_graph_size_and_update_options_window()

    def update_min_number_of_citations_two(self, adj):
        self.minNumberOfCitationsTwo = adj.value
        self.calculate_new_graph_size_and_update_options_window()

    def calculate_new_graph_size_and_update_options_window(self):
        # Count the number of articles with the required number of references and citations.
        nNodes = 0
        self.includedNodeNames = []
        self.excludedNodeNames = []
        for key in self.origNetworkCitations.keys():
            testOne = (
                self.origNetworkCitations[key] >= self.minNumberOfCitations and
                self.origNetworkReferences[key] >= self.minNumberOfReferences)
            testTwo = (
                self.origNetworkCitations[key] >= self.minNumberOfCitationsTwo
                and self.origNetworkReferences[key] >=
                self.min_mumber_of_references_two)
            if testOne or testTwo:
                nNodes += 1
                self.includedNodeNames.append(key)
            else:
                self.excludedNodeNames.append(key)

        self.citationmap.remove_named_nodes(self.excludedNodeNames)
        self.optionsWindow.graphSize = nNodes
        self.optionsWindow.labelGraphSize.set_text("Graph size: %d" % (nNodes))

    def show_options_window(self, action=None):
        try:
            self.optionsWindow.searchoptionswindow.destroy()
        except:
            pass

        self.optionsWindow = GuiOptionsWindow.GuiOptionsWindow(self.maxCitations, self.maxReferences)
        self.optionsWindow.adjMinNumberOfReferences.connect("value_changed", self.update_min_number_of_references)
        self.optionsWindow.adjMinNumberOfCitations.connect("value_changed", self.update_min_number_of_citations)
        self.optionsWindow.adjMinNumberOfReferencesTwo.connect("value_changed", self.update_min_number_of_references_two)
        self.optionsWindow.adjMinNumberOfCitationsTwo.connect("value_changed", self.update_min_number_of_citations_two)
        self.optionsWindow.showgraphbutton.connect("clicked", self.filter_and_show_current_citation_map, None)
        self.optionsWindow.exportgraphbutton.connect("clicked", self.export_eiltered_citation_map, None)
        self.optionsWindow.listofnodesbutton.connect("clicked", self.get_list_of_nodes, None)
        self.optionsWindow.ignoreArticlesButton.connect("clicked", self.ignore_articles_in_ban_file, None)
        self.calculate_new_graph_size_and_update_options_window()

    def on_open(self, action):
        chooser = gtk.FileChooserDialog(
            title="Open directory with bibliography",
            action=gtk.FILE_CHOOSER_ACTION_SELECT_FOLDER,
            buttons=(gtk.STOCK_CANCEL, gtk.RESPONSE_CANCEL, gtk.STOCK_OPEN,
                     gtk.RESPONSE_OK))
        chooser.set_default_response(gtk.RESPONSE_OK)
        if chooser.run() == gtk.RESPONSE_OK:
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
        print "<open_directory>"
        for currentFile in files:
            print "Parsing file: %s" % currentFile
            self.citationmap.parse_file(os.path.join(directory, currentFile))
        print "</open_directory>"
        self.update_orig_network()

    def update_orig_network(self):
        self.origNetworkPreFiltered = self.citationmap.graph.copy()
        self.origNetwork = self.origNetworkPreFiltered.copy()
        self.calculate_network_properties()

    def calculate_network_properties(self):
        self.origNetworkCitations = self.origNetwork.out_degree()
        self.origNetworkReferences = self.origNetwork.in_degree()
        assert (len(self.origNetworkCitations) ==
                len(self.origNetworkReferences))
        try:
            self.maxCitations = max(self.origNetworkCitations.values())
            self.maxReferences = max(self.origNetworkReferences.values())
        except:
            self.maxCitations = 20
            self.maxReferences = 20

    def filter_current_citation_map(self):
        self.citationmap.graph = self.origNetwork.copy()
        self.citationmap.analyze_graph()
        self.citationmap.remove_named_nodes(self.excludedNodeNames)

    def filter_and_export_current_citation_map(self):
        self.filter_current_citation_map()
        output = StringIO.StringIO()
        self.citationmap.output_graph(output, "BT")
        dotcode = output.getvalue()
        return dotcode

    def filter_and_show_current_citation_map(self, action, data):
        if self.optionsWindow.graphSize > 200:
            if not self.dialog_show_large_graph(self.optionsWindow.graphSize):
                return
        dotcode = self.filter_and_export_current_citation_map()
        self.mapview.set_dotcode(dotcode)
        self.mapview.zoom_to_fit()

    def dialog_show_large_graph(self, nNodes):
        self.quit_dialog = gtk.Dialog()

        # Set it modal and transient for main window.
        self.quit_dialog.set_modal(True)
        #self.quit_dialog.set_transient_for( self )

        # Set title
        self.quit_dialog.set_title('Confirmation')

        # Add buttons.
        self.quit_dialog.add_button(gtk.STOCK_YES, 1)
        self.quit_dialog.add_button(gtk.STOCK_NO, 2)

        # Create label
        label = gtk.Label(
            'Will you really visualize this huge graph? (# nodes = %d)' %
            nNodes)

        self.quit_dialog.vbox.pack_start(label)

        # Show dialog
        self.quit_dialog.show_all()

        # Run dialog
        response = self.quit_dialog.run()
        self.quit_dialog.hide()

        return response == 1

    def export_eiltered_citation_map(self, action, data):
        chooser = gtk.FileChooserDialog(
            title=None,
            action=gtk.FILE_CHOOSER_ACTION_SAVE,
            buttons=(gtk.STOCK_CANCEL, gtk.RESPONSE_CANCEL, gtk.STOCK_SAVE,
                     gtk.RESPONSE_OK))
        if chooser.run() == gtk.RESPONSE_OK:
            filename = chooser.get_filename()
            chooser.destroy()

            exportfile = open(filename, 'w')
            dotcode = self.filter_and_export_current_citation_map()
            exportfile.write(dotcode)
            exportfile.close()

        else:
            chooser.destroy()
        return False

    def get_list_of_nodes(self, action, data):
        listOfNodes = GuiListOfArticlesInGraph.GuiListOfArticlesInGraph()
        self.filter_current_citation_map()
        listOfNodes.nodesTreestore.clear()
        for key in self.citationmap.graphForAnalysis.nodes():
            try:
                networkCitations = self.origNetwork.out_degree(key)
                networkReferences = self.origNetwork.in_degree(key)
                article = self.citationmap.articles[key]
                year = int(article['PY'][0])
                fieldSO = string.join(article['SO'])
                fieldTitle = string.join(article['TI'])
                fieldAuthors = string.join(article['AU'], ' and ')
                fieldTC = int(article['TC'][0])
                fieldNR = int(article['NR'][0])
                listOfNodes.nodesTreestore.append(None,
                                                  [key, year, networkCitations,
                                                   networkReferences, fieldTC,
                                                   fieldNR, fieldSO,
                                                   fieldAuthors, fieldTitle])
            except KeyError:
                listOfNodes.nodesTreestore.append(None,
                                                  [key, -1, networkCitations,
                                                   networkReferences, -1, -1,
                                                   "", "", ""])

    def ignore_articles_in_ban_file(self, action, data):
        self.origNetwork = self.origNetworkPreFiltered.copy()
        filename = "%s/banlist" % self.openfilename
        try:
            file_handle = open(filename)
            for line in file_handle:
                article_identifier = line[:-1]
                try:
                    # Remove things that are only mentioned by the node
                    thingsReferenced = self.origNetwork.in_edges(
                        [article_identifier])
                    for edge in thingsReferenced:
                        referencedArticle = edge[0]
                        numberOfCitations = self.origNetwork.out_degree(
                            referencedArticle)
                        if (numberOfCitations == 1):
                            print referencedArticle
                            self.origNetwork.remove_node(referencedArticle)

                    # Remove node
                    print article_identifier
                    self.origNetwork.remove_node(article_identifier)
                except IOError:
                    pass
                except:
                    print "Unknown error detected"

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

    gtk.main()


if __name__ == '__main__':
    main()
