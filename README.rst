python-glob2
============

This is a version of Python's builtin glob module
(http://docs.python.org/library/glob.html) which captures the text matched
by glob patterns, and returns those matches alongside the filenames.


Example
-------

.. code-block:: python

    import glob2

    for filename, (version,) in glob2.iglob('./binaries/project-*.zip'):
        print version
