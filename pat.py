# -*- coding: utf-8 -*-
'''
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

Similar projects
----------------

- `parse <https://github.com/r1chardj0n3s/parse>`_
- `Lucidity <https://gitlab.com/4degrees/lucidity>`_
'''
__version__ = '0.1.0'
__author__ = 'Dan Bradham'
__url__ = 'https://github.com/danbradham/pat'
import string
import re
from collections import defaultdict

START = 0
END = 1
BOTH = 2
ANY = 3


class Template(object):
    '''
    Wraps a template string to provide parse functionality.

    Arguments:
        pattern (str): Python template string

    Attributes:
        pattern (str): template string
        fields (list): list of the template string's fields
        parsed_fields (list): List of data for each field
            [(field, group_name, field_regex, token, typ)...]
        regex (str): regex string used to perform parse

    Examples:
        >>> import pat
        >>> greeting = pat.Template('Hello {}!')
        >>> hello_world = greeting.format('world')
        >>> greeting.parse(hello_world)
        {0: 'world'}

        >>> path = pat.Template('assets/{asset_type}/{asset}')
        >>> path.parse('/mnt/Projects/assets/props/chair')
        {'asset_type': 'props', 'asset': 'chair'}
    '''

    _cache_ = {}
    group_regex = '(?P<{}>{})'
    first_regex = '(?:\w:/)?[\w_/]+'
    default_regex = '[\w_-]+'
    type_regex_map = {
        'b': '\d+',
        'c': '\w',
        'd': '[-+]?\d+',
        'o': '\d+',
        'x': '[0-9a-z]+',
        'X': '[0-9A-Z]+',
        'e': '\d*\.?\d+e[+-]\d+',
        'E': '\d*\.?\d+E[+-]\d+',
        'f': '[-+]?\d*\.?\d+',
        'F': '[-+]?\d*\.?\d+',
        'g': '[-+]?\d+|\-?inf|\-?0|nan|[-+]?\d*\.?\d+|\d*\.?\d+e[+-]\d+',
        'G': '[-+]?\d+|\-?inf|\-?0|nan|[-+]?\d*\.?\d+|\d*\.?\d+E[+-]\d+',
        'n': '[-+]?\d+|\-?inf|\-?0|nan|[-+]?\d*\.?\d+|\d*\.?\d+e[+-]\d+',
        '%': '\d*\.?\d+%'
    }
    type_map = {
        'b': lambda s: int(s, 2),
        'c': chr,
        'd': int,
        'o': lambda s: int(s, 8),
        'x': lambda s: int(s, 16),
        'X': lambda s: int(s, 16),
        'e': float,
        'E': float,
        'f': float,
        'F': float,
        'g': float,
        'G': float,
        'n': float,
        '%': lambda s: float(s.rstrip('%')) / 100.0
    }
    formatter = string.Formatter()

    def __new__(cls, pattern):
        if pattern not in cls._cache_:
            cls._cache_[pattern] = object.__new__(cls, pattern)
        return cls._cache_[pattern]

    def __init__(self, pattern):

        self.pattern = pattern
        self.parsed_fields = self._parse_pattern(pattern)
        self.regex = self._to_regex(pattern, self.parsed_fields)
        self.fields = [f[0] for f in self.parsed_fields]

    def _parse_pattern(self, pattern):

        fields = []
        auto = False
        manual = False
        pos_idx = 0
        field_idx = 0
        field_count = defaultdict(int)
        next_regex = self.first_regex

        for lit, field, spec, conv in self.formatter.parse(pattern):

            if field_idx > 0:
                next_regex = self.default_regex

            # Build original token
            token = '{' + field
            if conv:
                token += '!' + conv
            if spec:
                token += ':' + spec
            token += '}'

            # field and group name
            if not field:
                field = pos_idx
                group_name = 'POS' + str(pos_idx)
                if manual:
                    raise ValueError('Can not mix auto and manual numbering.')
                auto = True
                pos_idx += 1
            elif re.match('\d+', field):
                group_name = 'POS' + str(pos_idx)
                field = int(field)
                if auto:
                    raise ValueError('Can not mix auto and manual numbering.')
                manual = True
                pos_idx += 1
            else:
                group_name = field + str(field_count[field])
                field_count[field] += 1

            # Get type converter
            typ_char = None
            if spec:
                typ_char = spec[-1]
            typ = self.type_map.get(typ_char, None)

            # Create regex
            typ_regex = self.type_regex_map.get(typ_char, next_regex)
            field_regex = self.group_regex.format(group_name, typ_regex)
            fields.append((field, group_name, field_regex, token, typ))
            field_idx += 1

        return fields

    def _to_regex(self, pattern, fields):
        regex = re.escape(pattern)
        for field, group_name, field_regex, token, typ in fields:
            regex = regex.replace(re.escape(token), field_regex, 1)
        return regex

    def format(self, *args, **kwargs):
        '''Format this template using the provided *args and **kwargs

        See also:
            str.format()

        Returns:
            formatted string
        '''

        return self.pattern.format(*args, **kwargs)

    def parse(self, string, anchor=END):
        '''Parse a string using this template.

        Arguments:
            string (str) - String to parse
            anchor (int) - 0.START, 1.END, 2.BOTH, 3.ANY

        Returns:
            dict - the parsed data
        '''

        fields = self.parsed_fields
        regex = self.regex
        data = None

        if anchor == ANY:
            match = re.search(regex, string)
            if match:
                data = match.groupdict()
        else:
            if anchor == START:
                regex = '^' + regex
            elif anchor == END:
                regex += '$'

            match = re.match(regex, string)
            if match:
                data = match.groupdict()

        if data is None:
            return

        for field, group_name, field_regex, token, typ in fields:
            value = data.pop(group_name)
            if value:
                value = value.strip()
                if typ:
                    value = typ(value)
            data[field] = value

        return data


def parse(string, templates, anchor=END):
    '''Parse a string using a dict of templates and return the best parse.

    The best parse is the template that returned the most data.

    Examples:
        >>> parse('100%', {'percent': '{:0.2%}'})
        # 'percent', {0: 100.00}

    Arguments:
        string (str) - String to parse
        templates (dict) - Dictionary containing templates
        anchor (int) - 0.START, 1.END, 2.BOTH, 3.ANY

    Returns:
        (str, dict) - template key, parsed data
    '''

    best_parse = '', {}
    for name, tmpl in templates.items():

        if not isinstance(tmpl, Template):
            tmpl = Template(tmpl)

        data = tmpl.parse(string)

        if data and len(data.keys()) > len(best_parse[1].keys()):
            best_parse = name, data

    return best_parse
