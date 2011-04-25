import os
from os import path
import shutil
import tempfile

import glob2
from glob2 import fnmatch


class TestFnmatch(object):

    def test_filter_everything(self):
        names = (
            'fooABC', 'barABC', 'foo',)
        assert fnmatch.filter(names, 'foo*') == [
            ('fooABC', ('ABC',)),
            ('foo', ('',))
        ]
        assert fnmatch.filter(names, '*AB*') == [
            ('fooABC', ('foo', 'C')),
            ('barABC', ('bar', 'C'))
        ]

    def test_filter_single_character(self):
        names = (
            'fooA', 'barA', 'foo',)
        assert fnmatch.filter(names, 'foo?') == [
            ('fooA', ('A',)),
        ]
        assert fnmatch.filter(names, '???A') == [
            ('fooA', ('f', 'o', 'o',)),
            ('barA', ('b', 'a', 'r',)),
        ]

    def test_sequence(self):
        names = (
            'fooA', 'fooB', 'fooC', 'foo',)
        assert fnmatch.filter(names, 'foo[AB]') == [
            ('fooA', ('A',)),
            ('fooB', ('B',)),
        ]
        assert fnmatch.filter(names, 'foo[!AB]') == [
            ('fooC', ('C',)),
        ]


class TestGlob2(object):

    def setup(self):
        self.basedir = tempfile.mkdtemp()

    def teardown(self):
        shutil.rmtree(self.basedir)

    def makedirs(self, name):
        os.makedirs(path.join(self.basedir, name))

    def touch(self, name):
        open(path.join(self.basedir, name), 'w').close()

    def test(self):
        self.makedirs('dir1')
        self.makedirs('dir22')
        self.touch('dir1/a-file')
        self.touch('dir1/b-file')
        self.touch('dir22/a-file')
        self.touch('dir22/b-file')
        assert glob2.glob(path.join(self.basedir, 'dir?', 'a-*')) == [
            (path.join(self.basedir, 'dir1/a-file'), ('1', 'file'))
        ]


