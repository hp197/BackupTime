#!/usr/bin/python
# -*- encoding: utf-8 -*-
import unittest

class TestFo(unittest.TestCase):
	def test_bar(self):
		self.assertTrue(1 == 1)

if __name__ == '__main__':
    unittest.main()
