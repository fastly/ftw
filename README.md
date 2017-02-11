## Framework for Testing WAFs (FTW)
[![Build Status](https://travis-ci.org/fastly/ftw.svg?branch=master)](https://travis-ci.org/fastly/ftw)

##### Purpose
This project was created by researchers from ModSecurity and Fastly to help provide rigorous tests for WAF rules. It uses the OWASP Core Ruleset V3 as a baseline to test rules on a WAF. Each rule from the ruleset is loaded into a YAML file that issues HTTP requests that will trigger these rules.

Goals / Use cases include:

* Find regressions in WAF deployments by using continuous integration and issuing repeatable attacks to a WAF
* Provide a testing framework for new rules into ModSecurity, if a rule is submitted it MUST have corresponding positive & negative tests
* Evaluate WAFs against a common, agreeable baseline ruleset (OWASP)
* Test and verify custom rules for WAFs that are not part of the core rule set

## Installation
* `git clone git@github.com:fastly/ftw.git`
* `cd ftw`
* Make sure that pip is installed `apt-get install python-pip`
* `pip install -r requirements.txt`

## Running Tests with HTML contains and Status code checks only
* Create YAML files that point to your webserver with a WAF in front of it
* `py.test test/test_default.py --ruledir test/yaml`

## Provisioning Apache+Modsecurity+OWASP CRS
If you require an environment for testing WAF rules, there has been one created with Apache, Modsecurity and version 3.0.0 of the OWASP core ruleset. This can be deployed by:

* Checking out the repository: ``git clone https://github.com/fastly/waf_testbed.git``
* Typing ```vagrant up```

## Running Tests while overriding destination address in the yaml files to custom domain
* *start your test web server*
* `py.test test/test_default.py --ruledir=test/yaml --destaddr=domain.com
--port 443 --protocol https`

## Run integration test, local webserver, may have to use sudo
* `py.test test/integration/test_logcontains.py -s --ruledir=test/integration/`

## HOW TO INTEGRATE LOGS
1. Create a `*.py` file with the necessary imports, an example is shown in `test/integration/test_logcontains.py`
2. All functions with `test*` in the beginning will be ran by `py.test`, so make a function `def test_somewaf`
3. Implement a class that inherits `LogChecker`
  1. Implement the `get_logs()` function. FTW will call this function after it runs the test, and it will set datetimes of `self.start` and `self.end`
  2. Use the information from the datetime variables to retrieve the files from your WAF, whether its a file or an API call
  3. Get the logs, store them in an array of strings and return it from `get_logs()`
4. Make use of `py.test fixtures`. Use a function decorator `@pytest.fixture`, return your new `LogChecker` object. Whenever you use a function argument in your tests that matches the name of that `@pytest.fixture`, it will instantiate your object and make it easier to run tests. An example of this is in the python file from step 1.
5. Write a testing configuration in the `*.yaml` format as seen in `test/integration/LOGCONTAINSFIXTURE.yaml`, the `log_contains` line requires a string that is a regex. FTW will compile the `log_contains` string from each stage in the YAML file into a regex. This regex will then be used alongside the lines of logs passed in from `get_logs()` to look for a match. The `log_contains` string, then, should be a unique rule-id as FTW is greedy and will pass on the first match. False positives are mitigated from the start/end time passed to the `LogChecker` object, but it is best to stay safe and use unique regexes.
6. For each stage, the `get_logs()` function is called, so be sure to account for API calls if thats how you retrieve your logs.

## Making HTTP requests programmatically
Although it is preferred to make requests using the YAML format, often automated tests require making many dynamic requests. In such a case it is recommended to make use of the py.test framework in order to produce test cases that can be run as part of the whole.
Generally making an HTTP request is simple:
1. create an instance of the `HttpUA()` class
2. create an instance of the `Input()` class providing whatever parameters you don\'t want to be defaulted
3. provide the instance of the input class to `HttpUA.send_request()`

*For some examples see the http integration tests*
