#!/usr/bin/python
# -*- coding: utf-8 -*-
'''
    web tests (selenium webdriver tests)
'''

import pytaf_utils
from selenium import webdriver
from selenium.webdriver.common.desired_capabilities import DesiredCapabilities

def init_selenium(settings):
    browser = settings.get('browser','*chrome')
    selenium_host = settings.get('selenium_host','localhost')
    selenium_port = settings.get('selenium_port', '4444')
    version = settings.get('version', '10')
    platform = settings.get('platform', 'WINDOWS')
    driver = None
    dc = DesiredCapabilities()
    webdriver_url = "http://%s:%s/wd/hub" % (selenium_host, selenium_port)
    print("webdriver_url = %s" % webdriver_url)
    try:
        if browser.find("firefox") >= 0 or browser.find("*chrome") >= 0:
            dc = DesiredCapabilities.FIREFOX
            dc['version'] = version
            dc['platform'] = platform
            driver = webdriver.Remote(webdriver_url, dc)            
        elif browser.find("googlechrome") >= 0:
            dc = DesiredCapabilities.CHROME
            dc["chrome.switches"] = ["--ignore-certificate-errors"]
            driver = webdriver.Remote(webdriver_url, dc)
        elif browser.find("*mock") >= 0:
            dc = DesiredCapabilities.HTMLUNIT
            driver = webdriver.Remote(webdriver_url, dc)
        elif browser.find("android") >= 0:
            dc = DesiredCapabilities.ANDROID
            driver = webdriver.Remote(webdriver_url, dc)                             
        elif browser.find("*ie") >= 0:
            dc = DesiredCapabilities.INTERNETEXPLORER
            dc['version'] = version
            driver = webdriver.Remote(webdriver_url, dc)  
        else: # default to IE
            driver = webdriver.Remote(webdriver_url, dc)
    except:
        print(pytaf_utils.formatExceptionInfo())
    finally:    
        return driver
    
def test_web(args = {}):
    try:
        # initialize the error strings array
        errors = []

        # parse the global settings and test method params from the args provided
        settings = args['settings']
        params = args['params']

        # some selenium specific test stuff ...
        goto_url = params.get('url', 'http://www.google.com')
        driver = init_selenium(settings)
        driver.get(goto_url)
        element = driver.find_element_by_id('gbqfq')
        if element == None:
            errors.append('did not find the google input element')
        else:
            print('found the google input element')

        # call the utility method to verify the absence or errors or pack up the error messages if any
        return pytaf_utils.verify(len(errors) == 0, 'there were errors: %s' % errors)     
    except:
        # fail on any exception and include a stack trace
        return (False, pytaf_utils.formatExceptionInfo())
    finally:
        # cleanup
        driver.quit()