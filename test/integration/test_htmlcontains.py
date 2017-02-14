from ftw import ruleset, testrunner, http, errors
import pytest
import re
import random
import threading

def test_logcontains(ruleset, test):
    runner = testrunner.TestRunner()
    for stage in test.stages:
        runner.run_stage(stage)

# Should return a test error because its searching before response
def test_search1():
    runner = testrunner.TestRunner()
    x = ruleset.Input(dest_addr="example.com",headers={"Host":"example.com"})
    http_ua = http.HttpUA() 
    with pytest.raises(errors.TestError):    
        runner.test_response(http_ua.response_object,re.compile('dog'))

# Should return a failure because it is searching for a word not there
def test_search2():   
    runner = testrunner.TestRunner()
    x = ruleset.Input(dest_addr="example.com",headers={"Host":"example.com"})
    http_ua = http.HttpUA()
    http_ua.send_request(x)    
    with pytest.raises(AssertionError):   
        runner.test_response(http_ua.response_object,re.compile('dog'))

# Should return a success because it is searching for a word not there
def test_search3():
    runner = testrunner.TestRunner()
    x = ruleset.Input(dest_addr="example.com",headers={"Host":"example.com"})
    http_ua = http.HttpUA()
    http_ua.send_request(x)    
    runner.test_response(http_ua.response_object,re.compile('established to be used for'))

# Should return a success because we found our regex
def test_search4():   
    runner = testrunner.TestRunner()
    x = ruleset.Input(dest_addr="example.com",headers={"Host":"example.com"})
    http_ua = http.HttpUA()
    http_ua.send_request(x)      
    runner.test_response(http_ua.response_object,re.compile('.*'))
 
