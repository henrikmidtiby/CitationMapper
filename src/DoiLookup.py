#-------------------------------------------------------------------------------
# Name:        module1
# Purpose:
#
# Author:      hemi
#
# Created:     26-03-2014
# Copyright:   (c) hemi 2014
# Licence:     <your licence>
#-------------------------------------------------------------------------------


import httplib
import json

class DoiLookup:
    @classmethod
    def getDOIInformation(self, doi):
        print("Requesting information about %s" % doi)
        conn = httplib.HTTPConnection("data.crossref.org")
        headers = {"Accept": "application/vnd.citationstyles.csl+json"}
        conn.request("GET", "/" + doi, headers=headers)
        res = conn.getresponse()
        data = res.read()
        res.close()
        parsedData = json.JSONDecoder().decode(data)
        return parsedData

    @classmethod
    def showDOIInformation(self, doi):
        parsedData = getDOIInformation(doi)
        for k,v in parsedData.items():
            print("%s: %s" % (k, v))

        print("\n\n")

def main():
    showDOIInformation("10.1007/978-3-642-02674-4_9")
    showDOIInformation("10.1117/12.909861")

if __name__ == '__main__':
    main()
