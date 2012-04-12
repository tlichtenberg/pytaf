#!/usr/bin/python
# -*- coding: utf-8 -*-
#pylint: disable-msg=R0201,W0102,R0913,R0914,C0111,F0401,W0702
'''
    test utility methods
'''

import pymysql
from datetime import datetime
from datetime import date, timedelta
import sys
import traceback

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
    the_date = date.today() - timedelta(offset)
    datestr = the_date.strftime('%m%d%y')
    return datestr


def anystring_as_utf8(the_string):
    if type(the_string) is str:
        return the_string
    else:
        return the_string.encode('utf-8')


def str2bool(the_string):
    '''convert string to boolean
    '''
    return the_string.lower() in ("yes", "true", "t", "1")


def bool2str(the_bool=True):
    '''convert boolean to string
    '''
    if the_bool == True:
        return "true"
    else:
        return "false"


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
                if DEBUG:
                    print("test case params: ", params)
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


def get_all_tests(config, modules=[], load_test=False):
    '''
        get an array of all the test names in the config file

        for load tests, add the test name as many times as its load_mix value
        i.e. once for "load_mix = 1", zero for "load_mix = 0",
        10 for "load_mix = 10"
        this will determine the probability of the test being called
    '''
    module_names = []
    for module in modules:
        module_names.append(str(module.__name__))
    settings = config['settings']
    global_load_mix = settings.get("load_mix", 1)
    tests = []
    test_includes = config['tests']['includes']
    for i in range(0, len(test_includes)):
        # if this module is not to be included,
        # skip to the next test_includes item
        module = test_includes[i]['module']
        if module in module_names:
            included_methods = test_includes[i]['methods']
            for k in range(0, len(included_methods)):
                test_name = included_methods[k]['name']
                if load_test == True:
                    # params can override load_mix per test
                    params = included_methods[k]['params']
                    load_mix = params.get("load_mix", global_load_mix)
                    for i in range(int(load_mix)):
                        if DEBUG:
                            print('appending %s' % test_name)
                        tests.append(test_name)
                    load_mix = global_load_mix   # reset
                else:  # for non-load test. just add the test case!
                    if DEBUG:
                        print('appending %s' % test_name)
                    tests.append(test_name)
    return tests


def post_results(results=[], settings={}, db_config={},
                 total_passed=0, total_failed=0):
    print(settings, db_config, total_passed, total_failed)
    the_db = db_config.get('db', {})
    database = the_db.get("db_name", 'automation')
    host = the_db.get("db_host", 'localhost')
    user = the_db.get("db_user", 'root')
    password = the_db.get("db_password", '5ecre3t!')
    conn = pymysql.connect(db=database, host=host, user=user, passwd=password)
    mysql = conn.cursor()

    today = str(datetime.now())
    dates = today.rsplit(' ', 2)
    created_at = dates[0] + " " + dates[1]
    for i in range(0, len(results)):
        try:
            # required fields
            test_method = results[i]['test_method']
            module = results[i]['module']
            status = results[i]['status']
            message = results[i].get('message', '')
            sql = """ INSERT INTO test_results (test_method, module, status, message, date) VALUES ('%s', '%s', '%s', '%s', '%s') """ % (test_method, module, status, message, created_at)
            print(sql)
            mysql.execute(sql)
        except:
            print("SQL Error: %s" % formatExceptionInfo())
            continue

    mysql.close()
    conn.close()


def formatExceptionInfo(level=6):
    error_type, error_value, trbk = sys.exc_info()
    tb_list = traceback.format_tb(trbk, level)
    the_string = "Error: %s \nDescription: %s \nTraceback:" % (error_type.__name__,
                                                      error_value)
    for i in tb_list:
        the_string += "\n" + i
    return the_string
