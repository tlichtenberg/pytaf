#!/usr/bin/python
# -*- coding: utf-8 -*-

'''
    test utility methods
'''

import os
import http.client as httplib
import pymysql 
from datetime import datetime
from datetime import date, timedelta
import sys
import traceback
import time
import random
import _thread 
from operator import itemgetter

DEBUG = sys.flags.debug

def verify(expression, message):
    ''' called by tests for pass and fail '''
    print(expression)
    if expression == -1 or expression == False:
        error_message = message
        print("Error: %s" % error_message)
        return (False, error_message)
    else:
        error_message = ''
        return (True, error_message)
    
def get_date_string(offset=0):
    ''' get the date, offset in days (1 for yesterday, 2 for two days ago'''
    d = date.today() - timedelta(offset)
    datestr = d.strftime('%m%d%y')
    return datestr
   
def str2bool(v):
    '''convert string to boolean
    '''
    return v.lower() in ("yes", "true", "t", "1")

def bool2str(v=True):
    '''convert boolean to string
    '''
    if v:
        return "true"
    else:
        return "false"

def do_get(url, u, settings={}, https=True):
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
    headers = {"Content-type": content_type}
    if host != None: headers['host'] = host
    if cookie != None: headers['Set-Cookie'] = cookie
    start_time = time.time()
    conn.request("GET", u, '', headers)
    response = conn.getresponse()
    end_time = time.time()
    if DEBUG: print("http response time: (thr: %s, t: %s)" % (_thread.get_ident(), round(float(end_time - start_time),2)))
    if DEBUG: print(response.status, response.reason)
    d = response.read()
    if DEBUG: print(d)
    return { "data": d, "status": response.status, "reason": response.reason }

def do_post(url, u, request, settings = {}, https=True ):
    '''
        can be used for non multi-part posts      
   '''
    print("*** POST *** (thr: %s, t: %s) %s" % (_thread.get_ident(), time.time(), url + u))
    params = anystring_as_utf8(request)
    if DEBUG: print("params:", params)
    api_qa_cert = os.getenv("PYTAF_HOME") + "/resources/cert.pem"
    CERT_FILE = settings.get("cert_file", api_qa_cert) # os.getenv("PYTAF_HOME") + "/resources/cert.pem"
    host = settings.get('host',url)
    cookie = settings.get('cookie',None) 
    content_type = settings.get('content_type', "text/xml") 
    headers = {"Content-type": content_type}
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
    d = response.read()
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

def anystring_as_utf8(s,accept_utf8_input=False): # accept str or unicode, and output utf-8
    if type(s) is str:
        return s
    else:
        return s.encode('utf-8')

def get_params(config, test):
    ''' 
       get params for a test from the test config file
    '''
    # print "test: ", test
    test_includes = config['tests']['includes']
    for i in range(0, len(test_includes)):
        included_methods = test_includes[i]['methods']
        for k in range(0, len(included_methods)):
            test_name = included_methods[k]['name']
            if test_name == test:
                params = included_methods[k]['params']
                print("params: ", params)
                return params
    return None

def get_all_modules(config={}):
    ''' 
       get list of modules (python test files) from the test config file
    '''
    # print "test: ", test
    modules = []
    try:
        test_includes = config['tests']['includes']
        for i in range(0, len(test_includes)):
            modules.append(test_includes[i]['module'])
    except:
        pass
    return modules


def get_all_tests(config, modules=[], load_test = False):
    '''
        get an array of all the test names in the config file
        
        for load tests, add the test name as many times as its load_mix value
        i.e. once for "load_mix = 1", zero for "load_mix = 0", 10 for "load_mix = 10"
        this will determine the probability of the test being called
    '''
    module_names = []
    for m in modules:
        module_names.append(str(m.__name__))
    settings = config['settings']
    global_load_mix = settings.get( "load_mix", 1)
    tests = []
    test_includes = config['tests']['includes']
    for i in range(0, len(test_includes)):
        module = test_includes[i]['module']
        if module in module_names: # if this module is not to be included, skip to the next test_includes item              
            included_methods = test_includes[i]['methods']
            for k in range(0, len(included_methods)):
                test_name = included_methods[k]['name']
                if load_test == True:
                    params = included_methods[k]['params'] # params can override load_mix per test
                    load_mix = params.get("load_mix", global_load_mix)
                    for i in range(int(load_mix)):
                        if DEBUG: print('appending %s' % test_name)
                        tests.append(test_name)
                    load_mix = global_load_mix # reset
                else: # for non-load test. just add the test case!
                    if DEBUG: print('appending %s' % test_name)
                    tests.append(test_name)
    return tests


def post_results(results = [], settings = {}, total_passed = 0, total_failed = 0):
    global users
    
    database = 'automation'
    host = 'qa-jenkins' # '10.1.5.120' # 'qa-jenkins' 
    user = 'root'
    password = 'P@$$1ve'
    conn = pymysql.connect(db=database, host=host, user=user, passwd=password)
    mysql = conn.cursor()    
    
    browser = settings.get('browser', '')
    language = settings.get('language', 'english')
    player_version = settings.get('player_version', '')
    version = settings.get('version', '')
    lang = language[:2]
        
    t = str(datetime.now())
    dates = t.rsplit(' ', 2)
    created_at = dates[0] + " " + dates[1]
    for i in range(0, len(results)):
        try:
            # required fields
            test_method = results[i]['test_method']
            if len(browser) > 0: # append browser name to test_method, for django/mysql only, not testrail
                if browser.find("*chrome") > 0: browser = "firefox"
                browser = browser.replace('*', '')
                browser = browser.replace(' ', '_')
                test_method = "%s_%s_%s" % (test_method, browser, lang)
                results[i]['test_method'] = test_method # reset and pass along to test rail
            elif len(player_version) > 0: # append player_version to test_method, for django/mysql only, not testrail
                test_method = "%s_%s" % (test_method, player_version)
            
            module = results[i]['module']
            status = results[i]['status']
            # optional fields
            message = str(results[i].get('message','')) # could be Exception, hence the cast
            message = message.replace("'","")
            message = message.replace("\"","")
            message = message.replace("`","")
            # print message
            hbi = results[i].get('host_branch_api', '::')
            p = hbi.split(":")
            server = p[0]
            branch = p[1]
            test_class = p[2] # also api, currently unused
            # version = results[i].get('version', '') # version from settings
            reference = '' # for bug references to be added elsewhere
        
            sql = """ INSERT INTO regression_regression (server, branch, version, module, testClass, testMethod, status, message, reference, date)  VALUES ('%s', '%s', '%s', '%s', '%s', '%s', '%s', '%s', '%s', '%s') """ % (server, branch, version, module, test_class, test_method, status, message, reference, created_at)
            print(sql)
            mysql.execute(sql)
        except:
            print("SQL Error: %s" % formatExceptionInfo())
            continue
    
    mysql.close()
    conn.close()
    
def read_binary_file(filename):
    b = None
    f = open(filename, "rb")
    try:
        b = f.read()
    finally:
        f.close()
    return b
    
def append_to_file(filename, s):
    with open(filename, "a") as myfile:
        myfile.write(s)

def formatExceptionInfo(level = 6):
    error_type, error_value, trbk = sys.exc_info()
    tb_list = traceback.format_tb(trbk, level)    
    s = "Error: %s \nDescription: %s \nTraceback:" % (error_type.__name__, error_value)
    for i in tb_list:
        s += "\n" + i
    return s

def current_time_str_seconds():
    return str(int(time.time()))

def current_time_str():
    return str(int(time.time() * 1000))

def current_time():
    return int(time.time() * 1000)

def make_random_email_address():
    s = make_random_string(3,9) + "@" + make_random_string(6,12) + ".com"
    return s
     
def make_random_string(mn, mx):
    try:
        s = "QAa0bcLdUK2eHfJgTP8XhiFj61DOklNm9nBoI5pGqYVrs3CtSuMZvwWx4yE7zR"
        length = random.randint(mn, mx)
        sb = ""
        te = 0
        for i in range(0, length):
            te = random.randint(0, len(s) - 1)
            sb = sb + s[te]
        return sb 
    except Exception as inst:
        print('exception in make_random_string: %s' % inst)
        return ''

def list_includes(the_list=[], string_to_match='xxx'):
    for l in the_list:
        if l.find(string_to_match) >= 0:
            return True
    return False

def sort_dictionary(dict=None):
    ''' takes a dictionary and sorts it by value, returning a list of tuples
        e.g. foo =  foo = {'a': 2,'b': 4,'c': 3, 'd': 1}
             foo2 = ptest_utils.sort_dictionary(foo)
             print foo2 => [('d', 1), ('a', 2), ('c', 3), ('b', 4)]
        to print out the sorted list of tuples in reverse order, from highest to lowest value:
            for i in reversed(foo2):
                print i[0], i[1]
          =>
            b 4
            c 3
            a 2
            d 1
    '''
    if dict != None:
        sorted_array = sorted(dict.iteritems(), key=itemgetter(1))
        return sorted_array