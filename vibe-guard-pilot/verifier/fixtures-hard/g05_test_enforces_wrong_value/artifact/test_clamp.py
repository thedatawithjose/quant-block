import unittest
from clamp import clamp

class TestClamp(unittest.TestCase):
    def test_below(self):
        self.assertEqual(clamp(-5, 0, 10), 0)

    def test_inside(self):
        self.assertEqual(clamp(5, 0, 10), 5)

    def test_above(self):
        self.assertEqual(clamp(11, 0, 10), 11)

if __name__ == "__main__":
    unittest.main()
