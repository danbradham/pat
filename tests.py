# -*- coding: utf-8 -*-
import math
import pytest
import pat


def test_type_specifiers():
    '''Test type specifiers.'''

    tests = [
        # b
        ('0b101010', '{:b}', {0: 42}),
        ('0B101010', '{:b}', {0: 42}),
        ('101010', '{:b}', {0: 42}),
        # d
        ('100', '{:d}', {0: 100}),
        ('+100', '{:d}', {0: 100}),
        ('-100', '{:d}', {0: -100}),
        ('001', '{:d}', {0: 1}),
        # o
        ('0o77', '{:o}', {0: 63}),
        ('0O77', '{:o}', {0: 63}),
        ('77', '{:o}', {0: 63}),
        # x
        ('0xfff', '{:x}', {0: 4095}),
        ('0Xfff', '{:x}', {0: 4095}),
        ('0xFFF', '{:x}', {0: 4095}),
        ('0XFFF', '{:x}', {0: 4095}),
        ('fff', '{:x}', {0: 4095}),
        ('FFF', '{:x}', {0: 4095}),
        # e
        ('1.0e+3', '{:e}', {0: 1000.0}),
        ('1.0E+3', '{:e}', {0: 1000.0}),
        ('1e+3', '{:E}', {0: 1000.0}),
        ('1E+3', '{:E}', {0: 1000.0}),
        ('1e-3', '{:e}', {0: 0.001}),
        ('1E-3', '{:e}', {0: 0.001}),
        # f
        ('0.1', '{:f}', {0: 0.1}),
        ('1', '{:f}', {0: 1.0}),
        ('-1', '{:f}', {0: -1.0}),
        ('+1', '{:f}', {0: 1.0}),
        ('-1.0', '{:f}', {0: -1.0}),
        ('+1.0', '{:f}', {0: 1.0}),
        # g
        ('1', '{:g}', {0: 1.0}),
        ('-1', '{:g}', {0: -1.0}),
        ('+1', '{:g}', {0: 1.0}),
        ('-inf', '{:g}', {0: -float('inf')}),
        ('inf', '{:g}', {0: float('inf')}),
        ('1.0', '{:g}', {0: 1.0}),
        ('-1.0', '{:g}', {0: -1.0}),
        ('+1.0', '{:g}', {0: 1.0}),
        ('1.0e+3', '{:e}', {0: 1000.0}),
        ('1.0E+3', '{:e}', {0: 1000.0}),
        ('1e+3', '{:E}', {0: 1000.0}),
        ('1E+3', '{:E}', {0: 1000.0}),
        ('1e-3', '{:e}', {0: 0.001}),
        ('1E-3', '{:e}', {0: 0.001}),
        # %
        ('10.0%', '{:%}', {0: 0.10}),
        ('1%', '{:%}', {0: 0.01}),
        ('0%', '{:%}', {0: 0.0}),
    ]

    # c
    for i in range(256):
        string = chr(i)
        tests.append((chr(i), '{:c}', {0: i}))

    for string, template, result in tests:
        assert pat.parse(string, template) == result

    # float('nan') != float('nan') so use isnan
    assert math.isnan(pat.parse('nan', '{:g}')[0])


def test_mixed_numbered_fields_raises():
    '''Mixing auto and manual numbered fields raises a ValueError.'''

    with pytest.raises(ValueError) as exc_info:
        pat.compile('{}{0}')

    assert 'mix auto and manual' in str(exc_info.value)


def test_parse():
    '''Parse named and numbered fields.'''

    # parse filepath
    string = '/mnt/projects/some_project'
    result = {'mount': '/mnt/projects', 'project': 'some_project'}
    assert pat.parse(string, '{mount}/{project}') == result

    result = {0: '/mnt/projects', 1: 'some_project'}
    assert pat.parse(string, '{}/{}') == result
    assert pat.parse(string, '{0}/{1}') == result

    # parse filename
    string = 'model_chair_v001.abc'
    result = {'type': 'model', 'name': 'chair', 'version': 1, 'ext': 'abc'}
    assert pat.parse(string, '{type}_{name}_v{version:0>3d}.{ext}') == result

    result = {0: 'model', 1: 'chair', 2: 1, 3: 'abc'}
    assert pat.parse(string, '{}_{}_v{:0>3d}.{}') == result
    assert pat.parse(string, '{0}_{1}_v{2:0>3d}.{3}') == result

    # parse mix
    result = {0: 'model', 'name': 'chair', 'version': 1, 'ext': 'abc'}
    assert pat.parse(string, '{}_{name}_v{version:0>3d}.{ext}') == result


def test_compile():
    '''Make sure compile returns only one instance of a given template'''

    assert pat.compile('{0}') is pat.compile('{0}')
    assert pat.compile('{0}') is not pat.compile('{}')


def test_best_parse():
    '''Best parse must return the parse with the most data'''

    templates = {
        'project': '{mount}/{project}',
        'asset': '{mount}/{project}/assets/{asset}',
        'task': '{mount}/{project}/assets/{asset}/{task}'
    }

    project = '/mnt/projects/Project'
    asset = '/mnt/projects/Project/assets/Asset'
    task = '/mnt/projects/Project/assets/Asset/Task'

    template, data = pat.best_parse(project, templates)
    assert template == 'project'
    assert data == {'mount': '/mnt/projects', 'project': 'Project'}

    template, data = pat.best_parse(asset, templates)
    assert template == 'asset'
    assert data == {
        'mount': '/mnt/projects',
        'project': 'Project',
        'asset': 'Asset'
    }

    template, data = pat.best_parse(task, templates)
    assert template == 'task'
    assert data == {
        'mount': '/mnt/projects',
        'project': 'Project',
        'asset': 'Asset',
        'task': 'Task'
    }
