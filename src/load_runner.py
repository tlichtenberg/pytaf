import pytaf_utils
import random
from random import choice
import os
import datetime
import sys
import _thread
import time
import queue

DEBUG = sys.flags.debug


class LoadRunnerManager:
    ''' instantiates a ThreadPool object and adds LoadRunner
        instances to the pool's queue in accordance with the load test
        settings provided in the config file
    '''
    def __init__(self, config, tests):
        self.config = config
        self.settings = config['settings']
        self.url = self.settings['url']
        try:
            load_test_settings = self.settings['load_test_settings']
        except:
            print('error. load_test_settings were not found in the configuration: %s' % config)
            sys.exit(-1)
        self.max_threads = load_test_settings['max_threads']
        self.ramp_steps = load_test_settings['ramp_steps']
        self.ramp_interval = load_test_settings['ramp_interval']
        self.duration = load_test_settings['duration']
        self.throttle_rate = load_test_settings['throttle_rate']
        self.tests = tests
        self.tests_run = {}
        self.tests_passed = 0
        self.tests_failed = 0

    def passed(self):
        self.tests_passed = self.tests_passed + 1

    def failed(self):
        self.tests_failed = self.tests_failed + 1

    def start(self):
        ''' initializes a ThreadPool and then, while time is not yet up,
            periodically adds LoadRunner tasks to the ThreadPool's job queue
        '''
        initial_threads = self.max_threads / self.ramp_steps
        pool = ThreadPool(initial_threads)
        the_last_time = the_time = time.time()
        stop = the_last_time + int(self.duration)
        ramp_count = threads_started = initial_threads
        while the_time < stop:
            for n in range(self.max_threads):
                test = choice(self.tests)
                t = LoadRunner(self, self.config, test, self.throttle_rate)
                pool.addJob(t.run)
                # twiddle with this to control the rate
                time.sleep(float(self.throttle_rate) / 10.0)
                try:
                    t = self.tests_run[test]
                    self.tests_run[test] = t + 1
                except:
                    self.tests_run[test] = 1
                    continue
            time.sleep(float(self.throttle_rate))
            ''' add another chunk of threads if
                we haven't issued them all yet
            '''
            if self.ramp_steps > 1:
                if DEBUG:
                    print("threads_started = %s" % threads_started)
                if DEBUG:
                    print("ramp_count = %s" % ramp_count)
                if threads_started < self.max_threads \
                and ramp_count >= self.ramp_interval:
                    if DEBUG:
                        print("LoadRunnerManager: adding %s threads" %
                              initial_threads)
                    pool.addThreads(initial_threads)
                    ramp_count = 0
                    threads_started = threads_started + initial_threads
                else:
                    ramp_count = ramp_count + initial_threads

            the_time = time.time()
            print('thread pool queue size = %s' %
                  int(pool.getApproximateQueueSize()))
            print("LoadRunnerManager: time remaining: %s seconds" %
                  (stop - the_time))
        pool.stop()
        return self.tests_run, self.tests_passed, self.tests_failed


class LoadRunner():
    ''' each LoadRunner object invokes one test case as it is
        instantiated from the ThreadPool's task queue
        and returns the results to the LoadRunnerManager
    '''
    def __init__(self, manager, config, test, throttle_rate):
        self.manager = manager
        modules_array = pytaf_utils.get_all_modules(config)
        self.modules = map(__import__, modules_array)
        self.config = config
        self.settings = config['settings']
        self.test = test
        self.throttle_rate = throttle_rate
        self.results = []

    def run(self):
        params = pytaf_utils.get_params(self.config, self.test)
        if params != None:
            try:
                from pytaf import Pytaf
                self.pytaf = Pytaf()
                ''' instantiate the Pytaf.do_test method using reflection
                    and then invoke it with parameters '''
                methodToCall = getattr(Pytaf, 'do_test')
                result = methodToCall(self.pytaf, self.modules,
                                      self.settings, self.test, params)
                if result == True:
                    self.manager.passed()
                else:
                    self.manager.failed()
                amt = float(random.random() * self.throttle_rate)
                time.sleep(amt)
                return result
            except Exception as inst:
                print('LoadRunner.run exception: %s' % str(inst))
                time.sleep(float(self.throttle_rate))


class ThreadPool:
    "A pool of worker threads with tasks in its queue"
    def __init__(self, max_threads=10):
        self.queue = queue.Queue()
        self.threads = []
        self.stopping = False
        self.max_threads = max_threads

        # Start the initial threads, waiting on the empty Queue
        for i in range(int(self.max_threads)):
            self.threads.append(_thread.start_new_thread(self.threadFunction,
                                                         ()))

    def addThreads(self, num_threads=1):
        ''' adds more threads to the pool '''
        if DEBUG:
            print('ThreadPool: adding %s threads' % num_threads)
        self.max_threads = self.max_threads + num_threads
        for i in range(int(num_threads)):
            self.threads.append(_thread.start_new_thread(self.threadFunction,
                                                         ()))

    def addJob(self, function, *args, **kwargs):
        ''' puts a task into the queue '''
        try:
            if self.queue.qsize() < self.max_threads:
                self.queue.put((function, args, kwargs), False)
        except:
            pass  # queue is full, let it go

    def threadFunction(self):
        ''' fetches a task from the queue and invokes it '''
        while (not self.stopping):
            try:
                # don't block, throws exception if queue is full.
                task = self.queue.get(False)
                if (task != None):
                    function, args, kwargs = task
                    function(*args, **kwargs)
            except Exception as inst:
                pass  # queue is full, let it go

    def probablyIdle(self):
        return self.queue.empty()

    def getApproximateQueueSize(self):
        return self.queue.qsize()

    def stop(self):
        self.stopping = True
