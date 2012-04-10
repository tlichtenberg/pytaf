#!/usr/bin/python
# -*- coding: utf-8 -*-
'''
    library for api calls
'''
import os
import sys
import http.client as httplib
import urllib as urllib2
import urllib as urllib
import _thread
import time
import pytaf_utils
from bs4 import BeautifulSoup

DEBUG = sys.flags.debug

class ApiLib:
    
    def __init__(self):
        self.field = None
        
    def some_function(self):
        print("some function you got here!")
        return True
    
    def do_get(self, url, u, settings={}, headers={}, https=True):
        '''
            use for all get methods
            returns the response data        
        '''
        api_qa_cert = os.getenv("PYTAF_HOME") + "/resources/cert.pem"
        CERT_FILE = settings.get("cert_file", api_qa_cert)
        host = settings.get('host', url)
        cookie = settings.get('cookie',None) 
        content_type = settings.get('content_type', "text/xml") 
        print("*** GET *** (thr: %s, t: %s) %s" % (_thread.get_ident(), time.time(), url + u))
        if https == True:
            conn = httplib.HTTPSConnection(url, cert_file=CERT_FILE)
        else:
            conn = httplib.HTTPConnection(url)    
        headers["Content-type"] = content_type
        if host != None: headers['host'] = host
        if cookie != None: headers['Set-Cookie'] = cookie
        start_time = time.time()
        conn.request("GET", u, '', headers)
        response = conn.getresponse()
        end_time = time.time()
        if DEBUG: print("http response time: (thr: %s, t: %s)" % (_thread.get_ident(), round(float(end_time - start_time),2)))
        if DEBUG: print(response.status, response.reason)
        d = response.read().decode() # read() returns a bytes object
        if DEBUG: print(d)
        return { "data": d, "status": response.status, "reason": response.reason }
    
    def do_post(self, url, u, request, settings = {}, headers={}, https=True ):
        '''
            can be used for non multi-part posts      
       '''
        print("*** POST *** (thr: %s, t: %s) %s" % (_thread.get_ident(), time.time(), url + u))
        params = pytaf_utils.anystring_as_utf8(request)
        if DEBUG: print("params:", params)
        api_qa_cert = os.getenv("PYTAF_HOME") + "/resources/cert.pem"
        CERT_FILE = settings.get("cert_file", api_qa_cert) # os.getenv("PYTAF_HOME") + "/resources/cert.pem"
        host = settings.get('host',url)
        cookie = settings.get('cookie',None) 
        content_type = settings.get('content_type', "text/xml") 
        headers["Content-type"] = content_type
        if host != None: headers['host'] = host
        if cookie != None: headers['Set-Cookie'] = cookie
        if DEBUG: print(headers)
        if https == True:
            conn = httplib.HTTPSConnection(url, cert_file=CERT_FILE)
        else:
            conn = httplib.HTTPConnection(url)
        start_time = time.time()
        conn.request("POST", u, params, headers)
        response = conn.getresponse()
        end_time = time.time()
        if DEBUG: print("http response time: (thr: %s, t: %s)" % (_thread.get_ident(), round(float(end_time - start_time),2)))
        if DEBUG: print(response.status, response.reason) # , response.getheaders()
        d = response.read().decode() # read() returns a bytes object
        if DEBUG: print (d)
        return { "data": d, "status": response.status, "reason": response.reason }    
       
    def process_url(u):
        '''
            make the url python-http-happy
        '''
        if u.find("http://") >= 0:
            u = u[7:]
        if u.find("https://") >= 0:
            u = u[8:]
        return u
