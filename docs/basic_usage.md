# FTW Basic usage

This article describes how to use FTW with py.test. The first step is to setup your environment.

## Installation
If you don't have an environment to run your tests, you can set one up using vagrant:

```ruby
Vagrant.configure(2) do |config|
  config.ssh.forward_agent = true
  config.vm.provider 'virtualbox'
  config.vm.define 'waf' do |waf_conf|
    waf_conf.vm.box = 'ubuntu/xenial64'
  end
end
```
Once your vargant environment is up and running, you should update it and install python et al:

```
	% sudo apt-get update && sudo apt-get upgrade
	% sudo apt-get install python-pip
	% sudo pip install --upgrade pip
```

Next you will want to install FTW from github:

```
	sudo -H pip install git+https://github.com/fastly/ftw.git
```

## Building py.test file

Next you will need to setup a basic test file (`test_ftw_rule.py`) which implements the basic FTW test runner:

```python
#!/usr/bin/python
#
from ftw import ruleset, testrunner, http, errors
import pytest

def test_default(ruleset, test, destaddr):
    '''
        Default test with no log [logger] obj.
    '''
    runner = testrunner.TestRunner() 
    try:
        last_ua = http.HttpUA()
        for stage in test.stages:
            if destaddr is not None:
                stage.input.dest_addr = destaddr
            if stage.input.save_cookie:
                runner.run_stage(stage, http_ua=last_ua)
            else:
                runner.run_stage(stage, logger_obj=None, http_ua=None)
    except errors.TestError as e:
        e.args[1]['meta'] = ruleset.meta
        pytest.fail('Failure! Message -> {0}, Context -> {1}'.format(e.args[0],e.args[1]))
```

## Executing the tests

Next you will need a test file. This example pulls one of the SQL injection tests for the OWASP CRS. It should be noted that the test below expects to find an HTTP/WAF implementation on localhost. However there are fixtures defined in FTW and `py.test` which allows you to override certain variables.

```yaml
---
  meta:
    author: "Christian S.J. Peron"
    description: None
    enabled: true
    name: 942340.yaml
  tests:
  - 
    test_title: 942340-1
    desc: "basic SQL authentication bypass attempts 3/3"
    stages:
    - 
      stage:
        input:
          dest_addr: 127.0.0.1
          headers:
            Host: localhost
          method: GET
          port: 80
          # in ( select * from
          uri: "/?var=in%20%28%20select%20%2a%20from" 
          version: HTTP/1.0
        output:
          #
          # If the WAF is in blocking mode, we might want to
          # check for a 40X
          #
          status: 200
```
To execute this test, simply:

```
	% py.test test_ftw_rule.py --rule=942340.yaml
```

You can change the target web using using `--destaddr` for example:

```
	% py.test test_ftw_rule.py --rule=942340.yaml --destaddr=www.whatever.com
```
An example with output:

```
vagrant@ubuntu-xenial:~$ py.test test_ftw_rule.py --rule=942340.yaml --destaddr=www.whatever.com
====================================== test session starts =======================================
platform linux2 -- Python 2.7.12, pytest-2.9.1, py-1.5.2, pluggy-0.3.1
rootdir: /home/vagrant, inifile: 
plugins: ftw-1.1.0
collected 1 items 

test_ftw_rule.py .

==================================== 1 passed in 0.59 seconds ====================================
vagrant@ubuntu-xenial:~$ 
```
