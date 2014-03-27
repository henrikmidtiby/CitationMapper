#-------------------------------------------------------------------------------
# Name:        DoiLoopup
# Purpose:     Access information about articles identified by their doi.
#
# Author:      Henrik Skov Midtiby, hemi@mmmi.sdu.dk
#
# Created:     2014-03-26
# Copyright:   (c) Henrik Skov Midtiby, 2014
# Licence:     LGPL
#-------------------------------------------------------------------------------


import httplib
import json
import percache
import tempfile
import os
TESTFILE = os.path.join(tempfile.gettempdir(), "doilookup.cache")
cache = percache.Cache(TESTFILE, livesync=True)

@cache
def getDOIInformation(doi):
    print("Requesting information about %s" % doi)
    conn = httplib.HTTPConnection("data.crossref.org")
    headers = {"Accept": "application/vnd.citationstyles.csl+json"}
    conn.request("GET", "/" + doi, headers=headers)
    res = conn.getresponse()
    data = res.read()
    res.close()
    parsedData = json.JSONDecoder().decode(data)
    return parsedData

def showDOIInformation(doi):
    print("showDOIInformation('%s')" % doi)
    parsedData = getDOIInformation(doi)
    for k,v in parsedData.items():
        print("%-*s: %s" % (15, k, v))

    print("\n\n")

def main():
    showDOIInformation("10.1007/978-3-642-02674-4_9")
    showDOIInformation("10.1117/12.909861")
    showDOIInformation("10.1007/978-3-642-02674-4_9")

if __name__ == '__main__':
    main()
