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


