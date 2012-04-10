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
from load_runner import LoadRunnerManager

DEBUG = sys.flags.debug


class Pytaf:
    ''' Python3 test driver capable of running any arbitrary python
        methods in modules defined by json config files '''
    def __init__(self):
        ''' results object is used for collecting test results for output
            and database reporting '''
        self.results = []

    def setup(self, args):
        # Parse command line options
        parser = optparse.OptionParser()
        parser.add_option('-b', '--browser', default=None, type='string')
        parser.add_option('-c', '--config_file', default=None, type='string')
        parser.add_option('-d', '--db', default="false", type='string')
        parser.add_option('-e', '--excluded', default=None, type='string')
        parser.add_option('-l', '--logfile', default=None, type='string')
        parser.add_option('-m', '--modules', default=None, type='string')
        parser.add_option('-s', '--selenium_server', default=None,
                                                     type='string')
        parser.add_option('-t', '--test', default=None, type='string')
        parser.add_option('-u', '--url', default=None, type='string')
        parser.add_option('-y', '--test_type', default=None, type='string')
        parser.add_option('-z', '--loadtest_settings', default=None,
                                                       type='string')
        options, args_out = parser.parse_args(args)

        if options.config_file == None:
            print('-c (--config_file) is required')
            sys.exit(-1)

        if options.logfile != None:
            ''' redirect stdout to the logfile '''
            f = open(options.logfile, "a", 0)
            sys.stdout = f

        if options.excluded != None:
            ''' build a list of tests explicitly excluded from the
            command-line option '''
            excluded_list = options.excluded.split(',')
        else:
            excluded_list = None

        ''' load the config file '''
        try:
            config_path = os.getenv('PYTAF_HOME') + os.sep + "config" + os.sep
            f = open("%s%s" % (config_path, options.config_file), 'r').read()
            config = json.loads(f)
        except:
            print(pytaf_utils.formatExceptionInfo())
            print("problem with config file %s%s" %
                  (config_path, options.config_file))
            sys.exit()

        try:  # try to open the default db_config file
            f2 = open("%s%s" % (config_path, "db_config.json"), 'r').read()
            db_config = json.loads(f2)
        except:
            db_config = {}

        # command-line -u overrides config file for url
        if options.url != None:
            config['settings']['url'] = options.url  # for browser tests

        # command-line -b overrides config file for browser
        if options.browser != None:
            config['settings']['browser'] = options.browser

        # command-line -s option overrides the selenium_server
        # host and port settings
        if options.selenium_server != None:
            if options.selenium_server.find(":") >= 0:
                g = options.selenium_server.split(":")
                config['settings']['selenium_host'] = g[0]
                config['settings']['selenium_port'] = int(g[1])
            else:
                config['settings']['selenium_host'] = options.selenium_server

        # reset the settings object for passing on to test methods
        settings = config['settings']

        # dynamically import all modules found in the config file
        if options.modules == None:
            modules_array = pytaf_utils.get_all_modules(config)
        else:  # only load the specified module(s) from the config file
            modules_array = options.modules.split(",")
        if DEBUG:
            print('modules: %s' % modules_array)
        mapped_modules = map(__import__, modules_array)

        passed = 0
        failed = 0

        if options.test_type == 'load':
            '''
             the command-line may override load_test_settings with
             -z --loadtest_settings in the form of
             duration:max_threads:ramp_steps:ramp_interval:throttle_rate
             e.g. 3600:500:10:30:1
             which would run the load test for 1 hour (3600 seconds)
             ramping up to a total of 500 threads in 10 steps
             (each step would add 50 threads (500/10))
             and these batches of threads would be added in
             30 second installments (approximately)
             the final value (throttle_rate=1) is used to
             brake the entire load test operation by sleeping for
             that amount (in seconds) between chunks of test case allocations
            '''
            if options.loadtest_settings != None:
                p = options.loadtest_settings.split(":")
                if len(p) == 5:
                    config['settings']['load_test_settings'] = \
                    {"duration": int(p[0]),
                     "max_threads": int(p[1]),
                     "ramp_steps": int(p[2]),
                     "ramp_interval": int(p[3]),
                     "throttle_rate": int(p[4])}
                else:
                    print('load test settings are not complete.')
                    print('they must be in the form of' \
                'duration:max_threads:ramp_steps:ramp_interval:throttle_rate')
                    sys.exit(-1)
            # now start the load test
            passed, failed = self.do_load_test(mapped_modules, config)
        # if --test is specified, try and get the params and run each one
        elif options.test != None:
            ts = options.test.split(",")
            for i in range(0, len(ts)):
                test = ts[i]
                if self.test_excluded(test, excluded_list) == False:
                    params = pytaf_utils.get_params(config, test)
                    if params == None:
                        print("could not find params for test %s" % test)
                        sys.exit()
                    else:
                        status = self.do_test(mapped_modules, settings,
                                              test, params)
                        if status == True:
                            passed = passed + 1
                        else:
                            failed = failed + 1
                else:
                    print("%s is on the excluded list" % test)
        # if --test is not specified, collect and run all the
        # tests in the config file
        else:
            tests = pytaf_utils.get_all_tests(config, mapped_modules)
            for test in tests:
                if self.test_excluded(test, excluded_list) == False:
                    params = pytaf_utils.get_params(config, test)
                    if params != None:
                        status = self.do_test(mapped_modules, settings,
                                              test, params)
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
        for r in self.results:
            print_results.append(r['status'] + " " + r['test_method'])

        for r in sorted(print_results):
            print(r)

        # post results to the database
        if pytaf_utils.str2bool(options.db) == True:
            pytaf_utils.post_results(self.results, settings,
                                     db_config, passed, failed)

    def test_excluded(self, test, excluded_list):
        if excluded_list != None:
            for e in excluded_list:
                if test == e:
                    return True
        return False

    def do_test(self, modules, settings, test, params):
        result = (False, "error")
        start_time = end_time = elapsed_time = 0
        found_module = None
        test_was_found = False
        for m in modules:
            try:
                if DEBUG:
                    print("do test %s from module %s" % (test, m))
                methodToCall = getattr(m, test)
                found_module = str(m)
                test_was_found = True
                start_time = int(time.time())
                print("------------\n starting test: %s" % test)
                print(" start time:    %s" % datetime.datetime.now())
                print("------------")
                args = {"settings": settings, "params": params}
                result = methodToCall(args)
                end_time = int(time.time())
                elapsed_time = end_time - start_time
            except Exception as inst:
                if DEBUG:
                    print("exception from methodToCall: %s" %
                          sys.exc_info()[0])
                continue

        if test_was_found == False:
            print('error: pytaf did not find the test case (%s) \
            in the modules defined in the config file (%s)' %
            (test, str(modules)))
            return

        # tests return (True|False, String)
        error_message = str(result[1])  # could be Exception, hence the cast
        status = result[0]

        try:
            if status == True:  # any return value except False is PASSED
                status_string = "PASSED"
            else:
                status_string = "FAILED"

            module_string = ""
            if found_module != None:
                idx1 = found_module.rfind(os.sep) + 1
                idx2 = found_module.find(".py")
                module_string = found_module[idx1:idx2]

            self.results.append({"test_method":  test,
                                 "status": status_string,
                                 "message": error_message[:1024],
                                 "module": module_string})

            if status != False:
                result_str = "RESULT ===> PASSED: %s" % test
            else:
                result_str = "RESULT ===> FAILED: %s, %s" % \
                (test, pytaf_utils.anystring_as_utf8(error_message))
            if elapsed_time > 0:
                result_str = "%s, elapsed time: %s seconds" % \
                (result_str, str(elapsed_time))
            print("%s\n---------------" % result_str)
        except:
            print(pytaf_utils.formatExceptionInfo())

        return status

    def do_load_test(self, modules, config):
        '''
        intent is to run tests randomly (on multiple threads)
        calculated by threads and rate,
        for the period of duration (in minutes)
        '''
        # get a list of all the test method names from the config file
        tests = pytaf_utils.get_all_tests(config, modules, True)
        if DEBUG:
            print('found these tests: %s' % tests)

        manager = LoadRunnerManager(config, tests)
        tests_run, passed, failed = manager.start()

        count = 0
        for (total, completed) in tests_run.items():
            count = count + completed
            print(completed, total)
        print("------------\n%s tests run" % str(count))

        return passed, failed

if __name__ == "__main__":
    pytaf = Pytaf()
    pytaf.setup(sys.argv[1:])
