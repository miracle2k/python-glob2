python-glob2
============

This is an extended version of Python's builtin glob module
(http://docs.python.org/library/glob.html) which adds:

- The ability to capture the text matched by glob patterns, and
  return those matches alongside the filenames.

- A recursive '**' globbing syntax, akin for example to the ``globstar``
  option of the bash shell.


Example
-------

Matches being returned:

::

    import glob2

    for filename, (version,) in glob2.iglob('./binaries/project-*.zip', with_matches=True):
        print version


Recursive glob:

::

    >>> import glob2
    >>> all_header_files = glob2.glob('src/**/*.h')
    ['src/fs.h', 'src/media/mp3.h', 'src/media/mp3/frame.h', ...]


Note that ``**`` must appear on it's own as a directory
element to have its special meaning. ``**h`` will not have the
desired effect.

``**`` will match ".", so ``**/*.py`` returns Python files in the
current directory. If this is not wanted, ``*/**/*.py`` should be used
instead.
