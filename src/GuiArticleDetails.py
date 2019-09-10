#-------------------------------------------------------------------------------
# Name:        GuiArticleDetails
# Purpose:     Article details window for the citation mapper program
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

from gi.repository import GObject
import re
import gtk
import pprint
import io
import string
import webbrowser
import DoiLookup
import ArticleWithReferences


def open_url(widget, url):
    webbrowser.open(url)


# noinspection PyAttributeOutsideInit
class GuiArticleDetails(GObject.GObject):
    def __init__(self):
        self.__gobject_init__()
        self.doi = None
        self.node_scrolled_window = None
        self.node_information_window = gtk.Window()
        self.node_information_window.set_title("Article details")
        self.node_information_window.set_size_request(500, 300)
        self.vbox = gtk.VBox(False, 0)
        self.add_link_button()
        self.add_text_area()
        self.generate_node_scrolled_window()
        self.node_scrolled_window.show_all()
        self.add_request_doi_information_button()
        self.vbox.pack_start(self.node_scrolled_window, True, True, 0)
        self.node_information_window.add(self.vbox)
        self.node_information_window.show_all()
        gtk.link_button_set_uri_hook(open_url)

    def add_link_button(self):
        self.link_label = gtk.LinkButton("http://www.sdu.dk",
                                         label="Locate article on Web of Science")
        self.vbox.pack_start(self.link_label, False, False, 0)

    def citation_tag_event_handler(self, tag, widget, event, iter):
        if event.type == gtk.gdk.BUTTON_PRESS:
            end_iter = iter.copy()
            end_iter.forward_to_tag_toggle(self.citation_tag)
            iter.backward_to_tag_toggle(self.citation_tag)
            id_of_clicked_article = self.text_buffer.get_text(iter, end_iter)
            self.emit('citation_clicked', id_of_clicked_article)

    def add_text_area(self):
        self.text_tag_table = gtk.TextTagTable()
        self.text_buffer = gtk.TextBuffer(self.text_tag_table)
        self.text = gtk.TextView(self.text_buffer)
        self.text.set_wrap_mode(gtk.WRAP_WORD)
        self.citation_tag = gtk.TextTag()
        self.citation_tag.set_property('underline', True)
        self.citation_tag.connect('event', self.citation_tag_event_handler)
        self.text_tag_table.add(self.citation_tag)

    def add_request_doi_information_button(self):
        self.requestDOIInformation = gtk.Button(
            "Fetch more information based on DOI")
        self.requestDOIInformation.show()
        self.vbox.pack_start(self.requestDOIInformation, False, False, 5)
        self.requestDOIInformation.connect(
            "clicked", self.request_doi_information_callback, None)

    def request_doi_information_callback(self, p1, p2):
        text = DoiLookup.get_doi_information(self.doi)
        end_iterator = self.text_buffer.get_end_iter()
        self.text_buffer.insert(end_iterator, '\nDOI Information: \n')

        for k, v in text.items():
            end_iterator = self.text_buffer.get_end_iter()
            self.text_buffer.insert(end_iterator, "%-*s: %s\n" % (15, k, v))

        self.requestDOIInformation.hide()

    def generate_node_scrolled_window(self):
        self.node_scrolled_window = gtk.ScrolledWindow()
        self.node_scrolled_window.set_shadow_type(gtk.SHADOW_ETCHED_IN)
        self.node_scrolled_window.set_policy(gtk.POLICY_AUTOMATIC, gtk.POLICY_AUTOMATIC)
        self.node_scrolled_window.add(self.text)

    def update_article_information(self, url,
                                   citationmapbuild=None,
                                   article=None):
        print("update_article_information url = '%s'" % url)
        try:
            article = citationmapbuild.articles[url]
        except:
            print("Lookup failed")

        self.update_buttons(url)

        if isinstance(article, ArticleWithReferences.ArticleWithReferences):
            # TODO: Consider to make this an asynchronous call, as it feels like the GUI
            # TODO: does not respond when opening detailed information about a paper.
            # TODO: The delay is on the order of five seconds.
            article = self.use_doi_information(article)
            self.text_buffer.insert_at_cursor('%s\n' % url)
            self.text_buffer.insert_at_cursor('%d %s\n' % (int(article.year), article.firstAuthor))
            article.print_information()
            self.doi = article.doi
            self.text_buffer.insert_at_cursor('%s\n\n' % article.title)
            self.text_buffer.insert_at_cursor('Source: %s\n\n' % article.origin)
            self.text_buffer.insert_at_cursor('%s\n\n' % article.abstract)
            self.text_buffer.insert_at_cursor('ncites: %d\n' % article.ncites)
            self.text_buffer.insert_at_cursor('%s\n' % article.references)

            self.insert_graph_information(article, citationmapbuild.graph)

            self.list_citation_of_current_article(url, citationmapbuild.graph)
            self.list_references_of_current_article(url, citationmapbuild.graph)

            full_info_as_text = self.get_all_information_as_text(article)
            self.text_buffer.insert_at_cursor(
                '\nAll available information:\n%s' % full_info_as_text)
            return
        else:
            print("Not an article")

    def use_doi_information(self, article):
        try:
            doi_information = DoiLookup.get_doi_information(article.doi)
            article.title = doi_information['title']
            article.journal = doi_information['container-title']
        except:
            pass
        return article

    def get_all_information_as_text(self, article):
        all_knowledge_about_article = io.StringIO()
        pp = pprint.PrettyPrinter(stream=all_knowledge_about_article)
        pp.pprint(article)
        full_info_as_text = all_knowledge_about_article.getvalue()
        return full_info_as_text

    def update_buttons(self, url):
        pattern = re.compile(".*DOI (.*)")
        res = pattern.match(url)
        if (res):
            print(res.group(1))
            self.update_doi_information(res.group(1))
        else:
            self.link_label.set_uri("http://google.com/#q=%s" % url)
            self.link_label.set_label("Google this article")
            self.requestDOIInformation.hide()
            print("Not found")

    def insert_graph_information(self, article, graph):
        n_references_in_graph = graph.in_degree(article.id)
        n_citations_in_graph = graph.out_degree(article.id)
        self.text_buffer.insert_at_cursor(
            'Number of references in graph: %s\n' % n_references_in_graph)
        self.text_buffer.insert_at_cursor(
            'Number of citations in graph: %s\n' % n_citations_in_graph)

    def list_citation_of_current_article(self, url, graph):
        list_of_edges = graph.out_edges(url)
        end_iter = self.text_buffer.get_end_iter()
        self.text_buffer.insert(end_iter, "\nCited by\n")

        for edge in list_of_edges:
            self.insert_citation_with_proper_tag(edge[1])

    def list_references_of_current_article(self, url, graph):
        list_of_edges = graph.in_edges(url)
        end_iter = self.text_buffer.get_end_iter()
        self.text_buffer.insert(end_iter, "\nReferences\n")
        for edge in list_of_edges:
            self.insert_citation_with_proper_tag(edge[0])

    def insert_citation_with_proper_tag(self, edge):
        end_iter = self.text_buffer.get_end_iter()
        self.text_buffer.insert(end_iter, " * ")
        self.text_buffer.insert_with_tags(end_iter, "%s" % edge, self.citation_tag)
        self.text_buffer.insert(end_iter, "\n")

    def update_doi_information(self, doi):
        print("Updating doi information: %s" % doi)
        self.link_label.set_uri("http://dx.doi.org/%s" % doi)
        self.link_label.set_label("Open full text")
        self.doi = doi


GObject.type_register(GuiArticleDetails)
GObject.signal_new("citation_clicked", GuiArticleDetails, GObject.SIGNAL_RUN_FIRST,
                   GObject.TYPE_NONE, (GObject.TYPE_STRING,))


def main():
    GuiArticleDetails()
    gtk.main()


if __name__ == "__main__":
    main()
