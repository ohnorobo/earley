#!/usr/bin/python

import unittest
from earley import Rule, EarleyParser


# command line tests
'''
./earley.py grammar1.txt the president ate the pickle .
'''



class TestEarley(unittest.TestCase):

    def test_simple_grammar(self):

        rule_table1 = [
            Rule(0, "ROOT", ["S"], 0),
            Rule(0, "S", ["NP", "V"], 0),
            Rule(0, "S", ["NP", "VP"], 0),
            Rule(0, "VP", ["V", "NP"], 0),
            Rule(0, "NP", ["ADJ", "NP"],0),

            Rule(0, "NP", ["Jane"], 0),
            Rule(0, "ADJ", ["silly"], 0),
            Rule(0, "V", ["eats"], 0),
            Rule(0, "V", ["cries"], 0)
            ]

        earley = EarleyParser(rule_table1)

        self.assertEqual(True, earley.parse(["Jane", "eats"]))
        self.assertEqual(True, earley.parse(["Jane", "cries"]))
        self.assertEqual(False, earley.parse(["Jane"]))
        self.assertEqual(True, earley.parse(["silly", "Jane", "eats", "Jane"]))
        self.assertEqual(False, earley.parse(["Jane", "silly", "eats", "Jane"]))


    def test_complex_grammar(self):

        rule_table2 = [
            Rule(0, "ROOT", ["S"], 0),
            Rule(0, "S", ["NP", "VP"], 0),
            Rule(0, "NP", ["Det", "N"], 0),
            Rule(0, "NP", ["NP", "PP"], 0),
            Rule(0, "VP", ["V", "NP"], 0),
            Rule(0, "VP", ["VP", "PP"], 0),
            Rule(0, "PP", ["P", "NP"], 0),

            Rule(0, "NP", ["Papa"], 0),
            Rule(0, "N", ["caviar"], 0),
            Rule(0, "N", ["spoon"], 0),
            Rule(0, "V", ["ate"], 0),
            Rule(0, "P", ["with"], 0),
            Rule(0, "Det", ["the"], 0),
            Rule(0, "Det", ["a"], 0)
            ]

        earley = EarleyParser(rule_table2)

        self.assertEqual(True, earley.parse(["Papa", "ate", "the", "caviar", "with", "the", "spoon"]))
        self.assertEqual(True, earley.parse(["Papa", "ate", "the", "caviar"]))
        self.assertEqual(False, earley.parse(["ate", "the", "caviar", "with", "the", "spoon"]))
        self.assertEqual(False, earley.parse(["Papa", "ate", "caviar", "with", "the", "spoon"]))
        self.assertEqual(False, earley.parse(["Papa", "ate", "the", "caviar", "the", "spoon"]))
        self.assertEqual(False, earley.parse(["Papa", "the", "caviar", "with", "the", "spoon"]))
        self.assertEqual(False, earley.parse(["the", "caviar", "with", "the", "spoon"]))

    def test_cyclic_rules(self):

        rule_table = [
            Rule(0, "XP", ["YP"], 0),
            Rule(0, "YP", ["XP"], 0),
            Rule(0, "XP", ["a"], 0),
            Rule(0, "YP", ["b"], 0),
            ]

        earley = EarleyParser(rule_table)

        self.assertEqual(set(["a", "b"]), set(earley.left_corner["XP"]))
        self.assertEqual(set(["a", "b"]), set(earley.left_corner["YP"]))


    def test_tricyclic_rules(self):

        rule_table = [
            Rule(0, "XP", ["YP"], 0),
            Rule(0, "YP", ["ZP"], 0),
            Rule(0, "ZP", ["JP"], 0),
            Rule(0, "ZP", ["XP"], 0),
            Rule(0, "XP", ["a"], 0),
            Rule(0, "YP", ["b"], 0),
            Rule(0, "ZP", ["c"], 0),
            Rule(0, "KP", ["XP"], 0),
            Rule(0, "KP", ["d"], 0),
            Rule(0, "JP", ["e"], 0)
            ]

        earley = EarleyParser(rule_table)

        self.assertEqual(set(["a", "b", "c", "e"]), set(earley.left_corner["XP"]))
        self.assertEqual(set(["a", "b", "c", "e"]), set(earley.left_corner["YP"]))
        self.assertEqual(set(["a", "b", "c", "e"]), set(earley.left_corner["ZP"]))
        self.assertEqual(set(["a", "b", "c", "d", "e"]), set(earley.left_corner["KP"]))
        self.assertEqual(set(["e"]), set(earley.left_corner["JP"]))



if __name__ == '__main__':
    unittest.main()

