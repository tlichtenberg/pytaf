#!/usr/bin/python
# -*- coding: utf-8 -*-
#pylint: disable-msg=R0201,W0102,R0913,R0914,C0111,F0401,W0702
'''
    api tests
'''

import pytaf_utils
from apilib import ApiLib
import json
from bs4 import BeautifulSoup


def test_api(args={}):
    ''' generic test showing params and settings extraction from args '''
    settings = args['settingss']
    params = args['params']
    try:
        apilib = ApiLib()
        print(settings, params)
        apilib.some_function()
        return (True, '')
    except:
        return (False, pytaf_utils.formatExceptionInfo())


def test_html_get(args={}):
    ''' example using BeautifulSoup to parse html '''
    params = args['params']
    settings = args['settings']
    url = params.get('url',"www.google.com")
    try:
        errors = []
        headers = {}
        locator = "/index.html"
        lib = ApiLib()
        response = lib.do_get(url, locator, settings, headers, False)
        data = response['data']
        soup = BeautifulSoup(data)
        divs = soup.findAll('div')
        for div in divs:
            try:
                print("div style = %s" % div['style'])
            except:
                pass
        return pytaf_utils.verify(len(errors) == 0,
                                'there were errors: %s' % errors)
    except:
        return (False, pytaf_utils.formatExceptionInfo())


def test_simple_get(args={}):
    '''
        example of json parsing from http get
        http://httpbin.org/

        It echoes the data used in your request for any of these types:

        http://httpbin.org/ip Returns Origin IP.
        http://httpbin.org/user-agent Returns user-agent.
        http://httpbin.org/headers Returns header dict.
        http://httpbin.org/get Returns GET data.
        http://httpbin.org/post Returns POST data.
        http://httpbin.org/put Returns PUT data.
        http://httpbin.org/delete Returns DELETE data
        http://httpbin.org/gzip Returns gzip-encoded data.
        http://httpbin.org/status/:code Returns given HTTP Status code.
        http://httpbin.org/redirect/:n 302 Redirects n times.
        http://httpbin.org/cookies Returns cookie data.
        http://httpbin.org/cookies/set/:name/:value Sets a simple cookie.
        http://httpbin.org/basic-auth/:user/:passwd Challenges HTTPBasic Auth.
        http://httpbin.org/hidden-basic-auth/:user/:passwd 404'd BasicAuth.
        http://httpbin.org/stream/:n Streams n–100 lines.
        http://httpbin.org/delay/:n Delays responding for n–10 seconds.
'''
    params = args['params']
    settings = args['settings']
    url = params.get('url',"httpbin.org")
    try:
        errors = []
        headers = {}
        locator = "/get"
        lib = ApiLib()
        response = lib.do_get(url, locator, settings, headers, False)
        data = json.loads(response['data'])
        print(data)
        origin = data.get('origin', None)
        if origin == None:
            errors.append("did not get expected 'origin' field")
        else:
            print("origin = %s" % origin)

        return pytaf_utils.verify(len(errors) == 0,
                                  'there were errors: %s' % errors)
    except:
        return (False, pytaf_utils.formatExceptionInfo())


def test_simple_post(args={}):
    ''' example of json parsing from http post '''
    params = args['params']
    settings = args['settings']
    url = params.get('url',"httpbin.org")
    try:
        errors = []
        headers = {}
        request = ''
        locator = "/post"
        lib = ApiLib()
        response = lib.do_post(url, locator, request,
                               settings, headers, False)
        data = json.loads(response['data'])
        print(data)
        origin = data.get('origin', None)
        if origin == None:
            errors.append("did not get expected 'origin' field")
        else:
            print("origin = %s" % origin)

        return pytaf_utils.verify(len(errors) == 0,
                                  'there were errors: %s' % errors)
    except:
        return (False, pytaf_utils.formatExceptionInfo())
