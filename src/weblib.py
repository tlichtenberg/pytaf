#!/usr/bin/python
# -*- coding: utf-8 -*-
#pylint: disable-msg=R0201,W0102,R0913,R0914,C0111,F0401,W0702
from selenium import webdriver
from selenium.webdriver.common.desired_capabilities import DesiredCapabilities
import pytaf_utils

class WebLib:
    def __init__(self, settings):
        browser = settings.get('browser', '*firefox,10,Windows')
        browser_fields = browser.split(',')
        if len(browser_fields) == 3:
            browser_name = browser_fields[0]
            browser_version = browser_fields[1] 
            browser_platform = browser_fields[2]
        else:
            browser_name = browser_fields[0]
            browser_version = ''
            browser_platform = ''
        selenium_host = settings.get('selenium_host', 'localhost')
        selenium_port = settings.get('selenium_port', '4444')
        self.driver = None    
        webdriver_url = "http://%s:%s/wd/hub" % (selenium_host, selenium_port)
        print("webdriver_url = %s" % webdriver_url)
        try:
            if browser_name.find("firefox") >= 0 or browser_name.find("*chrome") >= 0:
                capabilities = DesiredCapabilities.FIREFOX              
            elif browser_name.find("*googlechrome") >= 0:
                capabilities = DesiredCapabilities.CHROME
                capabilities["chrome.switches"] = ["--ignore-certificate-errors"]
            elif browser_name.find("*mock") >= 0:
                capabilities = DesiredCapabilities.HTMLUNIT
            elif browser_name.find("android") >= 0:
                capabilities = DesiredCapabilities.ANDROID
            elif browser_name.find("*ie") >= 0:
                capabilities = DesiredCapabilities.INTERNETEXPLORER
            else:  # default to Firefox
                capabilities = DesiredCapabilities.FIREFOX
                             
            if browser_version != '':
                capabilities['version'] = browser_version
            if browser_platform != '':
                capabilities['platform'] = browser_platform
            self.driver = webdriver.Remote(webdriver_url, capabilities)
        except:
            print(pytaf_utils.formatExceptionInfo())
