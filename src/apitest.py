# -*- coding: UTF-8 -*-
'''
    api tests
'''

import pytaf_utils
from apilib import ApiLib
import json
from bs4 import BeautifulSoup

'''
    just go there, don't login
'''
def test_api(args = {}):
    # required test_config fields
    settings = args['settings']
    url = settings['url']
    
    try:
        apilib = ApiLib()
        apilib.some_function()
        return (True, '')
    except:
        return (False, pytaf_utils.formatExceptionInfo())
    
def test_html_get(args = {}):
    ''' example using BeautifulSoup to parse html '''
    settings = args['settings']
    url = settings['url']
    
    try:
        errors = []
        headers = {}
        url = "www.google.com"
        u = "/index.html"
        lib = ApiLib()
        response = lib.do_get(url, u, args['settings'], headers, False)
        data = response['data']
        soup = BeautifulSoup(data)
        divs = soup.findAll('div')
        for d in divs:
            try:
                print("div style = %s" % d['style'])
            except:
                pass
        return pytaf_utils.verify(len(errors) == 0, 'there were errors: %s' % errors)  
    except:
        return (False, pytaf_utils.formatExceptionInfo())
        
def test_testrail_api(args = {}):
    ''' example of testrail api '''
    settings = args['settings']
    params = args['params']
    try:
        results = []
        results.append({ "message": "", 
                    "status": "PASSED", 
                    "test_method": "test_channel_service_get_top_rated_no_token"
        })
         
        params["testrail_project"] = "Services"
        params["testrail_testplan"] = "Nightly_Automation_Web_Services"
        params["testrail_testrun"] = "Nightly_Automation_Web_Services"
        pytaf_utils.post_results_to_test_rail(results, params)
        return (True, '')
    except:
        return (False, pytaf_utils.formatExceptionInfo())
    
def test_simple_get(args = {}):
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
        http://httpbin.org/response-headers?key=val Returns given response headers.
        http://httpbin.org/redirect/:n 302 Redirects n times.
        http://httpbin.org/relative-redirect/:n 302 Relative redirects n times.
        http://httpbin.org/cookies Returns cookie data.
        http://httpbin.org/cookies/set/:name/:value Sets a simple cookie.
        http://httpbin.org/basic-auth/:user/:passwd Challenges HTTPBasic Auth.
        http://httpbin.org/hidden-basic-auth/:user/:passwd 404'd BasicAuth.
        http://httpbin.org/digest-auth/:qop/:user/:passwd Challenges HTTP Digest Auth.
        http://httpbin.org/stream/:n Streams n–100 lines.
        http://httpbin.org/delay/:n Delays responding for n–10 seconds.
'''
    try:
        errors = []
        headers = {}
        url = "httpbin.org"
        u = "/get"
        lib = ApiLib()
        response = lib.do_get(url, u, args['settings'], headers, False)
        data = json.loads(response['data'])
        print(data)
        origin = data.get('origin', None)
        if origin == None:
            errors.append("did not get expected 'origin' field")
        else:
            print("origin = %s" % origin)

        return pytaf_utils.verify(len(errors) == 0, 'there were errors: %s' % errors) 
    except:
        return (False, pytaf_utils.formatExceptionInfo())
    
def test_simple_post(args = {}):
    ''' example of json parsing from http post '''
    try:
        errors = []
        headers = {}
        request = ''
        url = "httpbin.org"
        u = "/post"
        lib = ApiLib()
        response = lib.do_post(url, u, request, args['settings'], headers, False)
        data = json.loads(response['data'])
        print(data)
        origin = data.get('origin', None)
        if origin == None:
            errors.append("did not get expected 'origin' field")
        else:
            print("origin = %s" % origin)

        return pytaf_utils.verify(len(errors) == 0, 'there were errors: %s' % errors) 
    except:
        return (False, pytaf_utils.formatExceptionInfo())