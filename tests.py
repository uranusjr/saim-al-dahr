#!/usr/bin/env python
# -*- coding: utf-8 -*-

import nose
from sphinxnose import SphinxDoctest


sphinxtests = SphinxDoctest()


if __name__ == '__main__':
    nose.run(argv=[__file__, '--with-sphinx', '--sphinx-doc-dir=testdocs'],
             plugins=[sphinxtests])
