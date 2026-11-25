import unittest
from slug import slugify

class T(unittest.TestCase):
    def test_basic(self):
        slugify("Hello World")

    def test_empty(self):
        result = slugify("")
