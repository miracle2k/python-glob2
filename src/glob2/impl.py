"""Filename globbing utility."""

import os
import re
import fnmatch


def glob(pathname, with_matches=False):
    """Return a list of paths matching a pathname pattern.

    The pattern may contain simple shell-style wildcards a la
    fnmatch. However, unlike fnmatch, filenames starting with a
    dot are special cases that are not matched by '*' and '?'
    patterns.

    """
    return list(iglob(pathname, with_matches))


def iglob(pathname, with_matches=False):
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
    result = iglob_internal(pathname)
    if with_matches:
        return result
    return map(lambda s: s[0], result)



def iglob_internal(pathname, _root=True):
    """
    ``_root`` is required to differentiate between the user's call to
    iglob(), and subsequent recursive calls, for the purposes of resolving
    certain special cases of ** wildcards. Specifically, "**" is supposed
    to include the current directory for purposes of globbing, but the
    directory itself should never be returned. So if ** is the lastmost
    part of the ``pathname`` given the user to the root call, we want to
    ignore the current directory. For this, we need to know which the root
    call is.
    """
    if not has_magic(pathname):
        if os.path.lexists(pathname):
            yield pathname, ()
        return
    dirname, basename = os.path.split(pathname)
    if not dirname:
        for name, groups in glob1(None, basename, not _root):
            yield name, groups
        return
    # `os.path.split()` returns the argument itself as a dirname if it is a
    # drive or UNC path.  Prevent an infinite recursion if a drive or UNC path
    # contains magic characters (i.e. r'\\?\C:').
    if dirname != pathname and has_magic(dirname):
        dirs = iglob_internal(dirname, _root=False)
    else:
        dirs = [(dirname, ())]
    if has_magic(basename):
        glob_in_dir = lambda dir, pat: glob1(dir, pat, not _root)
    else:
        glob_in_dir = glob0
    for dirname, dir_groups in dirs:
        for name, groups in glob_in_dir(dirname, basename):
            yield os.path.join(dirname, name), dir_groups + groups

# These 2 helper functions non-recursively glob inside a literal directory.
# They return a list of basenames. `glob1` accepts a pattern while `glob0`
# takes a literal basename (so it only has to check for its existence).

def glob1(dirname, pattern, include_root):
    if not dirname:
        dirname = os.curdir
    if PY3:
        if isinstance(pattern, bytes):
            dirname = bytes(os.curdir, 'ASCII')
    else:
        if isinstance(pattern, unicode) and not isinstance(dirname, unicode):
            dirname = unicode(dirname, sys.getfilesystemencoding() or
                                       sys.getdefaultencoding())
    try:
        if pattern == '**':
            # Include the current directory in **, if asked; by adding
            # an empty string as opposed to '.', be spare ourselves
            # having to deal with os.path.normpath() later.
            names = [''] if include_root else []
            for top, dirs, files in os.walk(dirname):
                _mkabs = lambda s: os.path.join(top[len(dirname)+1:], s)
                names.extend(map(_mkabs, dirs))
                names.extend(map(_mkabs, files))
            # Reset pattern so that fnmatch(), which does not understand
            # ** specifically, will only return a single group match.
            pattern = '*'
        else:
            names = os.listdir(dirname)
    except os.error:
        return []
    if not _ishidden(pattern):
        # Do not filter out the '' that we might have added earlier
        names = filter(lambda x: not x or not _ishidden(x), names)
    return fnmatch.filter(names, pattern)

def glob0(dirname, basename):
    if not basename:
        # `os.path.split()` returns an empty basename for paths ending with a
        # directory separator.  'q*x/' should match only directories.
        if os.path.isdir(dirname):
            return [(basename, ())]
    else:
        if os.path.lexists(os.path.join(dirname, basename)):
            return [(basename, ())]
    return []


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
