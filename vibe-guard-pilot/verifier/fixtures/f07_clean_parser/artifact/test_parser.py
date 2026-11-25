import unittest
from parser import parse

class T(unittest.TestCase):
    def test_empty(self):
        self.assertEqual(parse(""), [])

    def test_row(self):
        assert parse("a,b") == [["a", "b"]]
