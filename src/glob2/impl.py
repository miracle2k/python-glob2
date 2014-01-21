"""Filename globbing utility."""

from __future__ import absolute_import

import sys
import os
import re
from . import fnmatch


class Globber(object):

    listdir = staticmethod(os.listdir)
    isdir = staticmethod(os.path.isdir)
    islink = staticmethod(os.path.islink)
    exists = staticmethod(os.path.lexists)

    def walk(self, top, followlinks=False):
        """A simplified version of os.walk (code copied) that uses
        ``self.listdir``, and the other local filesystem methods.

        Because we don't care about file/directory distinctions, only
        a single list is returned.
        """
        try:
            names = self.listdir(top)
        except os.error as err:
            return

        items = []
        for name in names:
            items.append(name)

        yield top, items

        for name in items:
            new_path = os.path.join(top, name)
            if followlinks or not self.islink(new_path):
                for x in self.walk(new_path, followlinks):
                    yield x

    def glob(self, pathname, with_matches=False):
        """Return a list of paths matching a pathname pattern.

        The pattern may contain simple shell-style wildcards a la
        fnmatch. However, unlike fnmatch, filenames starting with a
        dot are special cases that are not matched by '*' and '?'
        patterns.

        """
        return list(self.iglob(pathname, with_matches))

    def iglob(self, pathname, with_matches=False):
        """Return an iterator which yields the paths matching a pathname
        pattern.

        The pattern may contain simple shell-style wildcards a la
        fnmatch. However, unlike fnmatch, filenames starting with a
        dot are special cases that are not matched by '*' and '?'
        patterns.

        If ``with_matches`` is True, then for each matching path
        a 2-tuple will be returned; the second element if the tuple
        will be a list of the parts of the path that matched the individual
        wildcards.
        """
        result = self._iglob(pathname)
        if with_matches:
            return result
        return map(lambda s: s[0], result)

    def _iglob(self, pathname, rootcall=True):
        """Internal implementation that backs :meth:`iglob`.

        ``rootcall`` is required to differentiate between the user's call to
        iglob(), and subsequent recursive calls, for the purposes of resolving
        certain special cases of ** wildcards. Specifically, "**" is supposed
        to include the current directory for purposes of globbing, but the
        directory itself should never be returned. So if ** is the lastmost
        part of the ``pathname`` given the user to the root call, we want to
        ignore the current directory. For this, we need to know which the root
        call is.
        """

        # Short-circuit if no glob magic
        if not has_magic(pathname):
            if self.exists(pathname):
                yield pathname, ()
            return

        # If no directory part is left, assume the working directory
        dirname, basename = os.path.split(pathname)

        # If the directory is globbed, recurse to resolve.
        # If at this point there is no directory part left, we simply
        # continue with dirname="", which will search the current dir.
        # `os.path.split()` returns the argument itself as a dirname if it is a
        # drive or UNC path.  Prevent an infinite recursion if a drive or UNC path
        # contains magic characters (i.e. r'\\?\C:').
        if dirname != pathname and has_magic(dirname):
            # Note that this may return files, which will be ignored
            # later when we try to use them as directories.
            # Prefiltering them here would only require more IO ops.
            dirs = self._iglob(dirname, rootcall=False)
        else:
            dirs = [(dirname, ())]

        # Resolve ``basename`` expr for every directory found
        for dirname, dir_groups in dirs:
            for name, groups in self.resolve_pattern(
                    dirname, basename, not rootcall):
                yield os.path.join(dirname, name), dir_groups + groups

    def resolve_pattern(self, dirname, pattern, globstar_with_root):
        """Apply ``pattern`` (contains no path elements) to the
        literal directory`` in dirname``.

        If pattern=='', this will filter for directories. This is
        a special case that happens when the user's glob expression ends
        with a slash (in which case we only want directories). It simpler
        and faster to filter here than in :meth:`_iglob`.
        """

        if sys.version_info[0] == 3:
            if isinstance(pattern, bytes):
                dirname = bytes(os.curdir, 'ASCII')
        else:
            if isinstance(pattern, unicode) and not isinstance(dirname, unicode):
                dirname = unicode(dirname, sys.getfilesystemencoding() or
                                           sys.getdefaultencoding())

        # If no magic, short-circuit, only check for existence
        if not has_magic(pattern):
            if pattern == '':
                if self.isdir(dirname):
                    return [(pattern, ())]
            else:
                if self.exists(os.path.join(dirname, pattern)):
                    return [(pattern, ())]
            return []

        if not dirname:
            dirname = os.curdir

        try:
            if pattern == '**':
                # Include the current directory in **, if asked; by adding
                # an empty string as opposed to '.', we spare ourselves
                # having to deal with os.path.normpath() later.
                names = [''] if globstar_with_root else []
                for top, entries in self.walk(dirname):
                    _mkabs = lambda s: os.path.join(top[len(dirname)+1:], s)
                    names.extend(map(_mkabs, entries))
                # Reset pattern so that fnmatch(), which does not understand
                # ** specifically, will only return a single group match.
                pattern = '*'
            else:
                names = self.listdir(dirname)
        except os.error:
            return []

        if not _ishidden(pattern):
            # Remove hidden files by default, but take care to ensure
            # that the empty string we may have added earlier remains.
            # Do not filter out the '' that we might have added earlier
            names = filter(lambda x: not x or not _ishidden(x), names)
        return fnmatch.filter(names, pattern)


default_globber = Globber()
glob = default_globber.glob
iglob = default_globber.iglob
del default_globber


magic_check = re.compile('[*?[]')
magic_check_bytes = re.compile(b'[*?[]')

def has_magic(s):
    if isinstance(s, bytes):
        match = magic_check_bytes.search(s)
    else:
        match = magic_check.search(s)
    return match is not None

def _ishidden(path):
    return path[0] in ('.', b'.'[0])
