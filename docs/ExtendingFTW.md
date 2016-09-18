Using FTW and integrating log_search with your WAF
===

It may be in your organization's best interest to use FTW as a library to run internal WAF tests that are not visible to the world. This can be due to sensitive information being present in WAF rules, policy and compliance or not revealing your defense tradecraft to adversaries. This is especially relevant for custom WAF rules tuned to your deployment.

If that is the case, it may be best to run FTW as a library. This is accomplished through an integration with FTW and `py.test`. This tutorial will show how one uses FTW as a python library, as well as creating a custom log search using the `log_contains` directive. Logs are ideal for confirmation of a WAF rule working due to the WAF generating a success or failure log and they can provide additional context surrounding the WAF rule trigger.

The rest of this tutorial will show how to setup a git project that installs ftw as a library, run a basic YAML test and finally integrate into a logging to find the presence of a WAF rule trigger.

If youd like to fork FTW and write tests and integrations from there, but keep it in a private repository, you can skip to Step 3. If youd like to use FTW as a library, proceed to Step 1.

Step 1 - Virtualenvironment, requirements.txt
==

`cd` to your directory where you want this project, then type `git init`.

Next, initiate a python virtual environment using `virtualenv env`, then drop into that environment `. env/bin/activate`.

Add `ftw` to `requirements.txt`

`pip install -r requirements.txt`

Done!


A note on py.test testing environment
---

`ftw` uses `py.test` as a way to do regression testing for WAFs. `py.test` is a powerful tool that helps make testing easier through a powerful command line tool interface, test parameterization and a rich API to help customize testing frameworks. You can read more about it [here](http://docs.pytest.org/en/latest/). 

`ftw` ships with a plugin to configure your `py.test` environment. This includes setting up informative test names in the console, command line arguments and helper functions. You can extend this further by writing your own [conftest.py](http://pytest.org/2.2.4/plugins.html) or submitting a P/R to `ftw` and change our `ftw/pytest_plugin.py`.  

Step 2 - Writing a test file
==

`touch test_foo.py`. `py.test` will be passed this file, and it will know to run any functions that start with `test_` within the file. So, for example, `def test_bar():` will be ran when the command `py.test test_foo.py` is issued. 

At the top of the file, import the necessary ftw modules. 
For those that installed `ftw` as a library, you can import `from ftw import ruleset, logchecker, testrunner`, but if you are writing a test directly in `ftw`, you need `ftw.ftw` in the `from ftw` line (for more examples of this, checkout one of the integration tests under `test/integration`)

Write the following function definition underneath the import:

```
def test_bar(ruleset, test):
    runner = testrunner.TestRunner()
    for stage in test.stages:
        runner.run_stage(stage)
 ```

This is the bare minimum you need to run `ftw` tests. `py.test` hooks into the `test_bar` function, then finds two arguments, `ruleset` and `test`. These are `py.test` fixtures, and essentially load YAML rules from the commandline, parameterize them and send them to this function. 

Spawn a local webserver on port 80 using `sudo pythom -m SimpleHTTPServer 80`. Then, make a `yaml` directory `mkdir yaml`. Copy the following `ftw yaml` configuration into `yaml/foo.yaml`

```
---
  meta: 
    author: "Foo"
    enabled: true
    name: "foo.yaml"
    description: "Description"
  tests: 
    - 
      rule_id: 1234
      stages: 
        - 
          stage: 
            input: 
              method: "GET"
              port: 80
              headers: 
                  User-Agent: "Foo"
                  Host: "localhost"
              protocol: "http"
              uri: "/"
            output: 
              status: 200
    - 
      rule_id: 1235
      stages: 
        - 
          stage: 
            input: 
              method: "GET"
              port: 80
              headers: 
                  User-Agent: "Foo"
                  Host: "localhost"
              protocol: "http"
              uri: "/fail.html"
            output: 
              status: 404

```

This YAML file has 2 tests with 1 stage each. The first test does a GET request to localhost on port 80 to the "/" URI, and expects a status 200. The second test does a GET request to localhost on port 80 to "/fail.html", and expects a 404 status. Each also set headers. You'll notice there is no `destaddr` directive, where you can put `localhost`, because there is a default to `localhost` in `ftw`. If you wish to go to another destination, add a `destaddr` directive under `input`. For examples, check out the integrations in `ftw`.

Step 3 - Run your test!
==
After you configured your `test_foo.py`, `conftest.py`, `yaml/foo.yaml` and you run your local webserver, run `py.test test_foo.py -s -v --rule=yaml/foo.yaml`.

The `-s -v` show stdout output and verbose test output, respectively.

You should see this output

```
└─[15:01]$ py.test test_foo.py -s -v --rule=./yaml/foo.yaml
============================================================ test session starts ============================================================
platform darwin -- Python 2.7.10, pytest-2.9.2, py-1.4.31, pluggy-0.3.1 -- /Users/zallen/git/ftw_test/env/bin/python
cachedir: .cache
rootdir: /Users/zallen/git/ftw_test, inifile:
collected 2 items

test_foo.py::test_bar[ruleset0-foo.yaml_ruleid_1234] PASSED
test_foo.py::test_bar[ruleset1-foo.yaml_ruleid_1235] PASSED

========================================================= 2 passed in 0.61 seconds =========================================================
```

2 tests were ran as specified in `foo.yaml`, and `py.test` shows verbose logging on which test was ran and what rule was ran. So we know `ruleid_1234` and `ruleid_1235` passed. If these errored out, you can investigate each rule to see what went wrong. 

These passed because the `output` directive in both rules specified an expected `status` directive. The webserver returned 200 and 404, respectively, and made the whole test suite passed. You can also pass in `html_contains: "^regex$"` to have FTW check for a pattern within the html_response.

Step 4 - Log integration
==

Although `status` and `html_contains` may be useful, it could give attackers information on how your WAF interacts with certain payloads. Because of this, you might want to be more stealthy in how you respond to certain payloads, but you still need to verify that the rules are firing. This is where the `log_contains` directive can be used to check your WAF logs.

If you add a `log_contains: "^regex$"` directive to the `output` field in yaml file, `ftw` will use that regex on a list of log lines to see if that pattern is present. The issue here is that you have to write the integration and send `ftw` the loglines for it to run the regex on. This makes `ftw` extendible because it can integrate with virtually any log system (API, filesystem) as long as you have programmatic access to it.

Here is how you integrate a log file into `ftw`.

The `logchecker` object you imported earlier is an abstract object that is passed into the TestRunner. Every `logchecker` object has an abstract function `get_logs()`. TestRunner in `ftw` will call this function everytime it sees a stage that contains `log_contains` directive. It expects the user to return an array of strings to perform the regex pattern check on.

Add `import pytest` to the top of your file.

Add the following class and `py.test` fixture function to your `test_foo.py` python file.

```
class FooLogChecker(logchecker.LogChecker):
    def get_logs(self):
        return []

@pytest.fixture
def logchecker_obj():
    """
    Returns a LoggerTest Integration object
    """
    return FooLogChecker()
```

Then update your `test_bar` function:

```
def test_bar(ruleset, test, logchecker_obj):
    runner = testrunner.TestRunner()
    for stage in test.stages:
        runner.run_stage(stage, logchecker_obj)
```

By adding `logchecker_obj` fixture to `test_bar`, `py.test` will call the `logchecker_obj()` fixture and return an instantiation of the `FooLogChecker` object. Now, everytime a test is ran with `log_contains`, `ftw` will call the `get_logs` function within that class.

Two instance variables exist in every `LogChecker` object, `self.start` and `self.end`. When a test is ran, `ftw` records the time in epoch time it started the input stage, and marks the time in epoch when the input stage is complete. You can reference these in `FooLogChecker` by accessing `self.start` and `self.end`. Use these to pull apart a logfile or send to an API to help filter out logs that were not in the time you issued the attack.

In `get_logs`, you can create a separate function that pulls apart a log file in modsecurity, or issues a search to an ELK stack that contains the logs from your WAF. 

Step 6 - YAML File
==
To confirm functionality of log_contains, return the following array of strings from `get_logs`

`['GET Request from foo', 'Trigger WAF rule-id-1234']`

Obviously, you would issue a search in a true deployment to wherever your logs are stored.

In `yaml/foo.yaml`, edit `rule_id: 1234` `output` field and add:

`log_contains: "rule-id-1234"`

It should look like this:
```
---
  meta: 
    author: "Foo"
    enabled: true
    name: "foo.yaml"
    description: "Description"
  tests: 
    - 
      rule_id: 1234
      stages: 
        - 
          stage: 
            input: 
              method: "GET"
              port: 80
              headers: 
                  User-Agent: "Foo"
                  Host: "localhost"
              protocol: "http"
              uri: "/"
            output: 
              status: 200
              log_contains: "rule-id-1234"
    - 
      rule_id: 1235
      stages: 
        - 
          stage: 
            input: 
              method: "GET"
              port: 80
              headers: 
                  User-Agent: "Foo"
                  Host: "localhost"
              protocol: "http"
              uri: "/fail.html"
            output: 
              status: 404
```

Run `py.test test_foo.py -s -v --rule=./yaml/foo.yaml`, you should see similar output:

```
└─[15:35]$ py.test test_foo.py -s -v --rule=./yaml/foo.yaml
============================================================ test session starts ============================================================
platform darwin -- Python 2.7.10, pytest-2.9.2, py-1.4.31, pluggy-0.3.1 -- /Users/zallen/git/ftw_test/env/bin/python
cachedir: .cache
rootdir: /Users/zallen/git/ftw_test, inifile:
collected 2 items

test_foo.py::test_bar[ruleset0-foo.yaml_ruleid_1234] PASSED
test_foo.py::test_bar[ruleset1-foo.yaml_ruleid_1235] PASSED

========================================================= 2 passed in 0.62 seconds =========================================================
```

Great! `ftw` loaded the tests, went to `ruleid_1234`, saw the `log_contains` directive, called the `get_logs()` function, was returned the list of 2 strings where one of them contained `rule-id-1234` and found that regex in your list. Now you have integration with `log_contains` working.
