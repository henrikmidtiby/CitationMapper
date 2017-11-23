#-------------------------------------------------------------------------------
# Name:        GuiArticleDetailsWindowHandler
# Purpose:     Class for handling several ArticleDetails windows.
#
# Author:      Henrik Skov Midtiby
#
# Created:     2011-10-11
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

import gobject
import GuiArticleDetails


class GuiArticleDetailsWindowHandler(gobject.GObject):
    def __init__(self):
        self.list_of_windows = []
        self.citationmap = None

    def article_clicked_in_details_window(self, placeholder_one, article_id, placeholder_two):
        self.open_new_article_details_window(article_id)

    def set_citationmap(self, citationmap_in):
        self.citationmap = citationmap_in

    def open_new_article_details_window(self, url):
        article_details_window = GuiArticleDetails.GuiArticleDetails()
        self.show_article_details(article_details_window, url)
        self.listen_to_signals_from_window(article_details_window)
        self.list_of_windows.append(article_details_window)

    def show_article_details(self, article_details_window, url):
        try:
            article = self.citationmap.articles[url]
            article_details_window.update_article_information(url, self.citationmap, article)
        except KeyError:
            print("openNewArticleDetailsWindow url = \'%s\'" % url)
            article_details_window.update_article_information(url, self.citationmap)

    def listen_to_signals_from_window(self, article_details_window):
        article_details_window.connect("citation_clicked", self.article_clicked_in_details_window, None)

    def close_all(self, action):
        for window in self.list_of_windows:
            window.node_information_window.destroy()
        self.list_of_windows = []


def main():
    pass


if __name__ == '__main__':
    main()
