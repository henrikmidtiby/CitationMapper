import unittest

import WebOfKnowledgeParser

class Test(unittest.TestCase):
    parser = WebOfKnowledgeParser.WebOfKnowledgeParser()

    def test_getYearFromIdentity_1(self):
        id = self.parser.getYearFromIdentity("VIENOT TC, 2007, LIB Q, V77, P157")
        self.assertEqual(id, 2007)

    def test_newIdentifierInspiredByWos2Pajek_1(self):
        id = self.parser.newIdentifierInspiredByWos2Pajek("VIENOT TC, 2007, LIB Q, V77, P157")
        self.assertEqual(id, "VIENOT TC,2007,V77,P157")

    def test_newIdentifierInspiredByWos2Pajek_2(self):
        cr_string = "Kalman R. E., 1960, J BASIC ENG, V82, P35, DOI [DOI 10.1115/1.3662552, 10.1115/1.3662552]"
        id = self.parser.newIdentifierInspiredByWos2Pajek(cr_string)
        self.assertEqual(id, "DOI 10.1115/1.3662552")

    def test_newIdentifierInspiredByWos2Pajek_3(self):
        cr_string = "O'Brien D, 2008, PROC SPIE, V7091, DOI 10.1117/12.799503"
        id = self.parser.newIdentifierInspiredByWos2Pajek(cr_string)
        self.assertEqual(id, "DOI 10.1117/12.799503")

