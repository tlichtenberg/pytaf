#!/usr/bin/python
# -*- coding: utf-8 -*-
'''
    web tests (selenium webdriver tests)
'''

import sys
import pytaf_utils
from weblib import WebLib
from selenium import webdriver
from selenium.webdriver.common.desired_capabilities import DesiredCapabilities

DEBUG = sys.flags.debug


def test_web(args={}):
    try:
        # initialize the error strings array
        errors = []

        # parse the global settings and test method
        # params from the args provided
        settings = args['settings']
        params = args['params']

        # do some selenium specific test stuff ...
        goto_url = params.get('url', 'http://www.google.com')
        lib = WebLib(settings)
        lib.driver.get(goto_url)
        element = lib.driver.find_element_by_id('gbqfq')
        if element == None:
            errors.append('did not find the google input element')
        else:
            print('found the google input element')

        # call the utility method to verify the absence or errors or
        # pack up the error messages if any
        return pytaf_utils.verify(len(errors) == 0,
                                  'there were errors: %s' % errors)
    except Exception as inst:
        if DEBUG:
            print(inst)
        # fail on any exception and include a stack trace
        return (False, pytaf_utils.formatExceptionInfo())
    finally:
        # cleanup
        lib.driver.quit()
