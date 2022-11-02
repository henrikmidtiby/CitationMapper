#-------------------------------------------------------------------------------
# Name:        Doi Look Up
# Purpose:     Access information about articles identified by their doi.
#
# Author:      Henrik Skov Midtiby, hemi@mmmi.sdu.dk
#
# Created:     2014-03-26
# Copyright:   (c) Henrik Skov Midtiby, 2014
# Licence:     LGPL
#-------------------------------------------------------------------------------

import http.client
import json
import percache
import tempfile
import os
cache_file = os.path.join(tempfile.gettempdir(), "doilookup.cache.db")
print(cache_file)
try:
    cache = percache.Cache(cache_file, livesync=True)
except Exception as e:
    print("An exception occured while creating an instance of percache")
    print("A solution could be to delete the cache file")
    print("Path to cache file: '%s'" % cache_file)
    print("Details about the exception")
    print(e)

@cache
def get_doi_information(doi):
    conn = http.client.HTTPConnection("api.crossref.org")
    conn.request("GET", "/v1/works/" + doi)
    res = conn.getresponse()
    data = res.read()
    #print(data)
    res.close()
    parsed_data = json.JSONDecoder().decode(data.decode('utf-8'))
    return parsed_data


def show_doi_information(doi):
    print("show_doi_information('%s')" % doi)
    parsed_data = get_doi_information(doi)
    print(json.dumps(parsed_data, indent = 3))

    print("\n\n")


def main():
    show_doi_information("10.1007/978-3-642-02674-4_9")
    show_doi_information("10.1117/12.909861")
    show_doi_information("10.1007/978-3-642-02674-4_9")


if __name__ == '__main__':
    main()
