import os
from os import path
import shutil
import tempfile

from nose.tools import assert_equals

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


class BaseTest(object):

    def setup(self):
        self.basedir = tempfile.mkdtemp()
        self._old_cwd = os.getcwd()
        os.chdir(self.basedir)

        self.setup_files()

    def setup_files(self):
        pass

    def teardown(self):
        os.chdir(self._old_cwd)
        shutil.rmtree(self.basedir)

    def makedirs(self, *names):
        for name in names:
            os.makedirs(path.join(self.basedir, name))

    def touch(self, *names):
        for name in names:
            open(path.join(self.basedir, name), 'w').close()


class TestPatterns(BaseTest):

    def test(self):
        self.makedirs('dir1', 'dir22')
        self.touch(
            'dir1/a-file', 'dir1/b-file', 'dir22/a-file', 'dir22/b-file')
        assert glob2.glob('dir?/a-*', True) == [
            ('dir1/a-file', ('1', 'file'))
        ]


class TestRecursive(BaseTest):

    def setup_files(self):
        self.makedirs('a', 'b', 'a/foo')
        self.touch('file.py', 'file.txt', 'a/bar.py', 'README', 'b/py',
                   'b/bar.py', 'a/foo/hello.py', 'a/foo/world.txt')

    def test_recursive(self):
        # ** includes the current directory
        assert_equals(sorted(glob2.glob('**/*.py', True)), [
            ('a/bar.py', ('a', 'bar')),
            ('a/foo/hello.py', ('a/foo', 'hello')),
            ('b/bar.py', ('b', 'bar')),
            ('file.py', ('', 'file')),
        ])

    def test_exclude_root_directory(self):
        # If files from the rot directory should not be included,
        # this is the syntax to use:
        assert_equals(sorted(glob2.glob('*/**/*.py', True)), [
            ('a/bar.py', ('a', '', 'bar')),
            ('a/foo/hello.py', ('a', 'foo', 'hello')),
            ('b/bar.py', ('b', '', 'bar'))
        ])

    def test_only_directories(self):
        # Return directories only
        assert_equals(sorted(glob2.glob('**/', True)), [
            ('a/', ('a',)),
            ('a/foo/', ('a/foo',)),
            ('b/', ('b',)),
        ])

    def test_parent_dir(self):
        # Make sure ".." can be used
        os.chdir(path.join(self.basedir, 'b'))
        assert_equals(sorted(glob2.glob('../a/**/*.py', True)), [
            ('../a/bar.py', ('', 'bar')),
            ('../a/foo/hello.py', ('foo', 'hello'))
        ])

    def test_fixed_basename(self):
        assert_equals(sorted(glob2.glob('**/bar.py', True)), [
            ('a/bar.py', ('a',)),
            ('b/bar.py', ('b',)),
        ])

    def test_all_files(self):
        # Return all files
        os.chdir(path.join(self.basedir, 'a'))
        assert_equals(sorted(glob2.glob('**', True)), [
            ('bar.py', ('bar.py',)),
            ('foo', ('foo',)),
            ('foo/hello.py', ('foo/hello.py',)),
            ('foo/world.txt', ('foo/world.txt',)),
        ])

    def test_root_directory_not_returned(self):
        # Ensure that a certain codepath (when the basename is globbed
        # with ** as opposed to the dirname) does not cause
        # the root directory to be part of the result.
        # -> b/ is NOT in the result!
        assert_equals(sorted(glob2.glob('b/**', True)), [
            ('b/bar.py', ('bar.py',)),
            ('b/py', ('py',)),
        ])

    def test_non_glob(self):
        # Test without patterns.
        assert_equals(glob2.glob(__file__, True), [
            (__file__, ())
        ])
        assert_equals(glob2.glob(__file__), [
            (__file__)
        ])
