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
        self.listOfWindows = []
        self.citationmap = None

    def article_clicked_in_details_window(self, placeholder_one, article_id, placeholder_two):
        self.openNewArticleDetailsWindow(article_id)

    def set_citationmap(self, citationmap_in):
        self.citationmap = citationmap_in

    def openNewArticleDetailsWindow(self, url):
        articleDetailsWindow = GuiArticleDetails.GuiArticleDetails()
        try:
            article = self.citationmap.articles[url]
            articleDetailsWindow.update_article_information(url, self.citationmap, article)
        except:
            print("openNewArticleDetailsWindow url = \'%s\'" % url)
            articleDetailsWindow.update_article_information(url, self.citationmap)
        articleDetailsWindow.connect("citation_clicked", self.article_clicked_in_details_window, None)
        self.listOfWindows.append(articleDetailsWindow)

    def closeAll(self, action):
        for window in self.listOfWindows:
            window.node_information_window.destroy()
        self.listOfWindows = []


def main():
    pass


if __name__ == '__main__':
    main()
