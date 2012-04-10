#!/usr/bin/python
# -*- coding: utf-8 -*-

from selenium import webdriver
from selenium.webdriver.common.desired_capabilities import DesiredCapabilities


class WebLib:
    def __init__(self, settings):
        browser = settings.get('browser', '*chrome')
        selenium_host = settings.get('selenium_host', 'localhost')
        selenium_port = settings.get('selenium_port', '4444')
        version = settings.get('version', '10')
        platform = settings.get('platform', 'WINDOWS')
        self.driver = None
        dc = DesiredCapabilities()
        webdriver_url = "http://%s:%s/wd/hub" % (selenium_host, selenium_port)
        print("webdriver_url = %s" % webdriver_url)
        try:
            if browser.find("firefox") >= 0 or browser.find("*chrome") >= 0:
                dc = DesiredCapabilities.FIREFOX
                dc['version'] = version
                dc['platform'] = platform
                self.driver = webdriver.Remote(webdriver_url, dc)
            elif browser.find("googlechrome") >= 0:
                dc = DesiredCapabilities.CHROME
                dc["chrome.switches"] = ["--ignore-certificate-errors"]
                self.driver = webdriver.Remote(webdriver_url, dc)
            elif browser.find("*mock") >= 0:
                dc = DesiredCapabilities.HTMLUNIT
                self.driver = webdriver.Remote(webdriver_url, dc)
            elif browser.find("android") >= 0:
                dc = DesiredCapabilities.ANDROID
                self.driver = webdriver.Remote(webdriver_url, dc)
            elif browser.find("*ie") >= 0:
                dc = DesiredCapabilities.INTERNETEXPLORER
                dc['version'] = version
                self.driver = webdriver.Remote(webdriver_url, dc)
            else:  # default to Firefox
                dc = DesiredCapabilities.FIREFOX
                self.driver = webdriver.Remote(webdriver_url, dc)
        except:
            print(pytaf_utils.formatExceptionInfo())
