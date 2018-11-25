pat
===
*Parseable Templates* for Python.

*pat* uses standard Python templates to parse data from strings. *pat* aims to
use common sense while also supporting as much of the string template
specification as possible. It supports both numbered and named fields and
performs type conversion for all field type specifiers.

What does it look like?
-----------------------

::

    >>> import pat
    >>> project = pat.compile('{mount}/{project}')
    >>> project.format(mount='/mnt/projects', project='My_Project')
    '/mnt/projects/My_Project'
    >>> project.parse('/mnt/projects/My_Project')
    {'mount': '/mnt/projects', 'project': 'My_Project'}

How does it work?
----------------
*pat* converts a template string into a regex with named capture groups based
on it's field names and type specifiers. The regex is used to retrieve data
from a string. Finally each bit of data retrieved is converted to the type
described by the field's spec.

::

    >>> floaty = pat.compile('{:0.2f}')
    >>> floaty.regex
    '(?P<POS0>[-+]?\d*\.?\d+)'
    >>> floaty.parse('100.10')
    {0: 100.10}

Similar projects
----------------

- `parse <https://github.com/r1chardj0n3s/parse>`_
- `Lucidity <https://gitlab.com/4degrees/lucidity>`_
