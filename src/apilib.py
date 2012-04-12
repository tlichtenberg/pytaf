#!/usr/bin/python
# -*- coding: utf-8 -*-
#pylint: disable-msg=R0201,W0102,R0913,R0914,C0111,F0401,W0702
'''
    library for api calls
'''
import os
import sys
import http.client as httplib
import _thread
import time
import pytaf_utils

DEBUG = sys.flags.debug


class ApiLib:

    def __init__(self):
        self.field = None

    def some_function(self):
        print("this is one dandy function you got here!")
        return True

    def do_get(self, url, locator, settings={}, headers={}, https=True):
        '''
            use for all get methods
            returns the response data
        '''
        api_qa_cert = os.getenv("PYTAF_HOME") + "/resources/cert.pem"
        certificate_file = settings.get("cert_file", api_qa_cert)
        host = settings.get('host', url)
        cookie = settings.get('cookie', None)
        content_type = settings.get('content_type', "text/xml")
        print("*** GET *** (thr: %s, t: %s) %s" %
              (_thread.get_ident(), time.time(), url + locator))
        if https == True:
            conn = httplib.HTTPSConnection(url, cert_file=certificate_file)
        else:
            conn = httplib.HTTPConnection(url)
        headers["Content-type"] = content_type
        if host != None:
            headers['host'] = host
        if cookie != None:
            headers['Set-Cookie'] = cookie
        start_time = time.time()
        conn.request("GET", locator, '', headers)
        response = conn.getresponse()
        end_time = time.time()
        if DEBUG:
            print("http response time: (thr: %s, t: %s)" %
                (_thread.get_ident(), round(float(end_time - start_time), 2)))
        if DEBUG:
            print(response.status, response.reason)
        data = response.read().decode()  # read() returns a bytes object
        if DEBUG:
            print(data)
        return {"data": data, "status": response.status,
                 "reason": response.reason}

    def do_post(self, url, locator, request, settings={}, 
                headers={}, https=True):
        '''
            can be used for non multi-part posts
       '''
        print("*** POST *** (thr: %s, t: %s) %s" %
             (_thread.get_ident(), time.time(), url + locator))
        params = pytaf_utils.anystring_as_utf8(request)
        if DEBUG:
            print("params:", params)
        api_qa_cert = os.getenv("PYTAF_HOME") + "/resources/cert.pem"
        certificate_file = settings.get("cert_file", api_qa_cert)
        host = settings.get('host', url)
        cookie = settings.get('cookie', None)
        content_type = settings.get('content_type', "text/xml")
        headers["Content-type"] = content_type
        if host != None:
            headers['host'] = host
        if cookie != None:
            headers['Set-Cookie'] = cookie
        if DEBUG:
            print(headers)
        if https == True:
            conn = httplib.HTTPSConnection(url, cert_file=certificate_file)
        else:
            conn = httplib.HTTPConnection(url)
        start_time = time.time()
        conn.request("POST", locator, params, headers)
        response = conn.getresponse()
        end_time = time.time()
        if DEBUG:
            print("http response time: (thr: %s, t: %s)" %
                 (_thread.get_ident(), round(float(end_time - start_time), 2)))
        if DEBUG:
            print(response.status, response.reason)  # response.getheaders()
        data = response.read().decode()  # read() returns a bytes object
        if DEBUG:
            print (data)
        return {"data": data, "status": response.status,
                "reason": response.reason}

    def process_url(self, url):
        '''
            make the url python-http-happy by stripping off the front part
        '''
        if url.find("http://") >= 0:
            url = url[7:]
        if url.find("https://") >= 0:
            url = url[8:]
        return url
