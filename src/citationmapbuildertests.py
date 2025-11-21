# -*- coding: utf-8 -*-
"""
Created on Thu Mar 27 09:17:49 2014

@author: henrik
"""

import unittest
import WebOfKnowledgeParser


class MyTest(unittest.TestCase):
    def test(self):
        wokp = WebOfKnowledgeParser.WebOfKnowledgeParser()
        self.assertEqual(
            wokp.newIdentifierInspiredByWos2Pajek(
                "PARZEN E, 1962, ANN MATH STAT, V33, P1065, DOI 10.1214/aoms/1177704472"
            ),
            "DOI 10.1214/aoms/1177704472",
        )
        self.assertEqual(
            wokp.newIdentifierInspiredByWos2Pajek("VIENOT TC, 2007, LIB Q, V77, P157"),
            "VIENOT TC,2007,V77,P157",
        )
        self.assertEqual(
            wokp.newIdentifierInspiredByWos2Pajek("OLANDER B, 2007, INFORM RES, V12"),
            "OLANDER B,2007,V12",
        )
        self.assertEqual(
            wokp.newIdentifierInspiredByWos2Pajek("FRION P, 2009, P68"),
            "FRION P,2009,P68",
        )
        self.assertEqual(wokp.newIdentifierInspiredByWos2Pajek(""), "")


if __name__ == "__main__":
    unittest.main()
