pat
===
*Parseable Templates* for Python.

*pat* Templates are like standard python string templates but can also be used
to parse strings. *pat* tries to parse strings using common sense and support
as much of the string format spec as possible.

Features:

    - Supports named and positional fields
    - Intelligently converts parsed data to Python types
    - Caches templates to speed up repeat uses

What does it look like?
-----------------------
*pat* Templates look exactly like Python string templates.

::

    >>> import pat
    >>> project = pat.Template('{mount}/{project}')
    >>> path = project.format(mount='/mnt/projects', project='My_Project')
    >>> project.parse(path)
    {'mount': '/mnt/projects', 'project': 'My_Project'}

How does it work?
----------------
*pat* converts a string template into a regex with named capture groups based
on it's field names and specs. The regex is used to retrieve data from a
string. Finally each bit of data retrieved is converted to the type described
by the field's spec.

::

    >>> floaty = pat.Template('{:0.2f}')
    >>> floaty.regex
    '(?P<POS0>[-+]?\d*\.?\d+)'
    >>> floaty.parse('100.10')
    {0: 100.10}

As you can see, the float spec has been used to convert to an applicable
regex and also convert the parsed string data back to the expected type.

What about X?
----------------------
All of the similar libraries I've seen do not support enough of the Python
string format spec, or use a modified spec, making them hard to remember. *pat*
tries to do what you expect and supports only the standard string format spec,
making it more familiar and easier to remember.
