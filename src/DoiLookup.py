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
TESTFILE = os.path.join(tempfile.gettempdir(), "doilookup.cache.db")
print(TESTFILE)
cache = percache.Cache(TESTFILE, livesync=True)


@cache
def get_doi_information(doi):
    conn = http.client.HTTPConnection("data.crossref.org")
    headers = {"Accept": "application/vnd.citationstyles.csl+json"}
    conn.request("GET", "/" + doi, headers=headers)
    res = conn.getresponse()
    data = res.read()
    res.close()
    parsed_data = json.JSONDecoder().decode(data.decode('utf-8'))
    return parsed_data


def show_doi_information(doi):
    print("show_doi_information('%s')" % doi)
    parsed_data = get_doi_information(doi)
    for k, v in parsed_data.items():
        print("%-*s: %s" % (15, k, v))

    print("\n\n")


def main():
    show_doi_information("10.1007/978-3-642-02674-4_9")
    show_doi_information("10.1117/12.909861")
    show_doi_information("10.1007/978-3-642-02674-4_9")


if __name__ == '__main__':
    main()
