'''
    test driver
'''

import os
import sys
sys.path.append(os.getenv('PYTAF_HOME'))
import optparse
import json
import pytaf_utils
import time
import datetime
import _thread

DEBUG = sys.flags.debug
results = []
    
'''
    main entry point from command-line
'''
def main():
    # Parse command line options
    parser = optparse.OptionParser()
    parser.add_option('-b', '--browser', default=None, type='string')
    parser.add_option('-c', '--config_file', default=None, type='string')
    parser.add_option('-d', '--db', default="false", type='string')
    parser.add_option('-e', '--excluded', default=None, type='string')
    parser.add_option('-l', '--logfile', default=None, type='string')
    parser.add_option('-m', '--modules', default=None, type='string')
    parser.add_option('-t', '--test', default=None, type='string')  
    parser.add_option('-u', '--url', default=None, type='string')    
    options, args = parser.parse_args()

    if options.config_file == None:
        print('-c (--config_file) is required')
        sys.exit(-1)
        
    browser = options.browser
    modules = options.modules
    test = options.test
    url = options.url
    
    if options.logfile != None:
        ''' redirect stdout to the logfile '''
        f = open(options.logfile, "a", 0)
        sys.stdout = f
    
    if options.excluded != None:
        excluded_list = options.excluded.split(',') # array of excluded test method names
    else:
        excluded_list = None
    
    try:
        config_path = os.getenv('PYTAF_HOME') + os.sep + "config" + os.sep
        f = open("%s%s" % (config_path,options.config_file), 'r').read()
        config = json.loads(f)                             
    except:
        print(pytaf_utils.formatExceptionInfo())
        print("problem with config file %s%s" % (config_path, options.config_file))
        sys.exit()
     
    # pass along write_to_db and webdriver in settings   
    config['settings']['write_to_db'] = pytaf_utils.str2bool(options.db)   
           
    # command-line -u overrides config file for url
    if url != None: 
        config['settings']['url'] = url # for browser tests
        
    # command-line -b overrides config file for browser
    if browser != None:
        config['settings']['browser'] = browser

    settings = config['settings']    
        
    # dynamically import all modules found in the config file
    if modules == None:
        modules_array = pytaf_utils.get_all_modules(config)
    else: # only load the specified module(s) from the config file
        modules_array = modules.split(",")
    mapped_modules = map(__import__, modules_array)
    
    passed = 0
    failed = 0
   
    if test != None:  # if --test is specified, try and get its params and run it
        if test.find(",") >= 0: # multiple tests
            ts = test.split(",")
            for i in range(0, len(ts)):
                test = ts[i]
                if test_excluded(test, excluded_list) == False: 
                    params = pytaf_utils.get_params(config, test)
                    if params == None:
                        print("could not find params for test %s" % test)
                        sys.exit()
                    else:
                        status = do_test(mapped_modules, settings, test, params)
                        if status == True:
                            passed = passed + 1
                        else:
                            failed = failed + 1
                else:
                    print("%s is on the excluded list" % test)
        else: # just one test
            if test_excluded(test, excluded_list) == False: 
                params = pytaf_utils.get_params(config, test)
                if params == None:
                    print("could not find params for test %s" % test)
                    sys.exit()
                else:
                    status = do_test(mapped_modules, settings, test, params)
                    if status == True:
                        passed = passed + 1
                    else:
                        failed = failed + 1
            else:
                print("%s is on the excluded list" % test)
    else: # if --test is not specified, collect and run all the tests in the config file
        tests = pytaf_utils.get_all_tests(config, mapped_modules)
        for test in tests:
            if test_excluded(test, excluded_list) == False: 
                params = pytaf_utils.get_params(config, test)
                if params != None:
                    status = do_test(mapped_modules, settings, test, params)
                    if status == True:
                        passed = passed + 1
                    else:
                        failed = failed + 1
            else:
                print("%s is on the excluded list" % test)
                 
    print("---------------")
    print("Tests Run: %s" % (passed + failed))
    print("Passed:    %s" % passed)
    print("Failed:    %s" % failed)
            
    print_results = []
    for r in results:
        print_results.append(r['status'] + " " + r['test_method'])
        
    for r in sorted(print_results):
        print(r)
                      
    # post results to the database
    if pytaf_utils.str2bool(options.db) == True:
        pytaf_utils.post_results(results, settings, passed, failed)

        
def test_excluded(test, excluded_list):
    if excluded_list != None:
        for e in excluded_list:
            if test == e:
                return True
    return False
    
def do_test(modules, settings, test, params):
    result = (False, "error")
    start_time = end_time = elapsed_time = 0
    found_module = None
    test_was_found = False
    for m in modules:
        try:
            # if DEBUG: print "do test %s from module %s" % (test, m)
            methodToCall = getattr(m, test)
            found_module = str(m)
            test_was_found = True
            start_time = int(time.time())
            print("------------\n starting test: %s" % test)
            print(" start time:    %s" % datetime.datetime.now())
            print("------------")
            args = { "settings": settings, "params": params }
            result = methodToCall(args)
            end_time = int(time.time())
            elapsed_time = end_time - start_time
            if DEBUG: print("result: %s" % result)
        except:
            #if DEBUG: print "exception from methodToCall"
            #if DEBUG: print sys.exc_info()[0]
            continue
        
    if test_was_found == False:
        print('error: pytaf did not find the test case (%s) in the modules defined in the config file (%s)' % (test, str(modules)))
        return
   
    # tests return (True|False, String)
    error_message = str(result[1]) # could be Exception, hence the cast
    status = result[0]
            
    try:                  
        if status == True: # any return value except False is PASSED
            status_string = "PASSED"
        else:
            status_string = "FAILED"
        
        module_string = ""
        if found_module != None:
            idx1 = found_module.rfind(os.sep) + 1  
            idx2 = found_module.find(".py") 
            module_string = found_module[idx1:idx2]
            
        results.append({ "test_method":  test, "status": status_string, "message": error_message[:1024], "module": module_string})
            
        if status != False:
            result_str = "RESULT ===> PASSED: %s" % test
        else:
            result_str = "RESULT ===> FAILED: %s, %s" % (test, pytaf_utils.anystring_as_utf8(error_message))
        if elapsed_time > 0:
            result_str = result_str +  ", elapsed time: %s seconds" % str(elapsed_time)
        print("%s\n---------------" % result_str)
    except:
        print(pytaf_utils.formatExceptionInfo())
        
    return status
                                 
if __name__ == "__main__":
    # Starts and initializes the web server when web_gevent.py is invoked by python
    main()

    
