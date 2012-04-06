#!/usr/bin/python
# -*- coding: utf-8 -*-
'''
    api tests
'''

import pytaf_utils
from apilib import ApiLib

def test_api(args = {}):
    # required test_config fields
    settings = args['settings'] 
    params = args['params']
    try:
        apilib = ApiLib()
        apilib.some_function()
        return (True, '')
    except:
        return (False, pytaf_utils.formatExceptionInfo())
    
def test_exclude(args = {}):
    # required test_config fields
    settings = args['settings'] 
    params = args['params']
    try:
        print("this test is supposed to be excluded")
        return (True, '')
    except:
        return (False, pytaf_utils.formatExceptionInfo())