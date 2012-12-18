# Copyright (c) 2012 Alain Fischer (alain [dot] fischer [at] bluewin [dot] ch)
# Licensed under the terms of the MIT License
# see: http://www.opensource.org/licenses/mit-license.php

# implementation based on first OMeta/JS:
# http://tinlizzie.org/ometa/ometa-js-old/

__author__ = 'alain'

import unittest
import ometa_old

class OMetaExampleTestCase(unittest.TestCase):
    def test_number(self):
        self.assertEqual(ometa_old.OMetaExample().matchAllWith('123', 'number'), 123)

    def test_expr(self):
        self.assertEqual(ometa_old.OMetaExample().matchAllWith('(12-(34+2)*2)/3', 'expr'), -20)

if __name__ == '__main__':
    unittest.main()
