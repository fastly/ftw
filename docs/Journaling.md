# Journaling


FTW supports the process of creating journal entries for your HTTP tests. The idea behind this stems from the need to decouple the sending of attacks with testing the responses. This might be better explained with the following use cases:

 1. A pentester needs to issue attacks against a WAF but does not have access to the logs at the time of the test/series of attacks. A journal of attack requests and responses will help the pentester by correlating a database of FTW requests and responses with customer logs at a later time.
 
 2. A security engineer integrating FTW into their WAF environment does not want to check each FTW attack/response pair against a log. This is especially painful for cases where logs are sent to a network service and the tool _beats_ the log service by checking for a log as its being sent, being indexed etc. This is not ideal because we run into a halting problem where we cannot guess ahead of time how long to wait before we check the log service for the existence of a log. With this method, the security engineer can fire off an attack and then batch check the logs at a later date when he or she knows they can query a window of time without having to worry about network latency.  

Workflow
==================
The workflow is twofold. Run the FTW tool `build_journal.py` against a service with a WAF in front of it and collect response data. Once all of the response data is retrieved, run FTW as you would in any other integration scenario, but write a plugin that opens the sqlite database to retrieve logs instead of a file or a network API.

Usage - Build the Journal
==================

1. `git clone git@github.com:fastly/ftw.git`
2. `virtualenv ftwenv`
3. `./ftwenv/bin/activate`
4. `pip install -r requirements.txt`
5. `./tools/build_journal.py --ruledir dir`   
  * This will produce `journal.sqlite`
  * Check out the options in `build_journal.py` for specifying journal files, table names

Once these steps are complete, you will have a `sqlite` file that you can explore and query by rule-id, time etc. 


Usage - Using the Journal 
==================

Because FTW was built with intention of custom integrations, testers can follow similar steps of found in Step 4 of `ExtendingFTW.md`.

A new API in the rulerunner was created to pass in journal files to run FTW against. The testrunner will still need the `logchecker_obj` to call `get_logs()`, since it is correlating sqlite output with log output. Implement a logchecker just like the ones outlined in `ExtendingFTW.md`, and FTW will handle retrieving the correct logs from sqlite for you.

We will use an example from `SpiderLabs/OWASP-CRS-regressions` as the example:

```python
from ftw import ruleset, logchecker, testrunner
import pytest
import sys
import re
import os
import ConfigParser

def test_crs(ruleset, test, logchecker_obj, with_journal, tablename):
    runner = testrunner.TestRunner()
    for stage in test.stages:
        runner.run_stage_with_journal(test.ruleset_meta['name'], test, with_journal, tablename, logchecker_obj)

class FooLogChecker(logchecker.LogChecker):

    def reverse_readline(self, filename):
        with open(filename) as f:
            f.seek(0, os.SEEK_END)
            position = f.tell()
            line = ''
            while position >= 0:
                f.seek(position)
                next_char = f.read(1)
                if next_char == "\n":
                    yield line[::-1]
                    line = ''
                else:
                    line += next_char
                position -= 1
            yield line[::-1]

    def get_logs(self):
        import datetime
        config = ConfigParser.ConfigParser()
        config.read("settings.ini")
        log_location = config.get('settings', 'log_location')
        our_logs = []
        pattern = re.compile(r"\[([A-Z][a-z]{2} [A-z][a-z]{2} \d{1,2} \d{1,2}\:\d{1,2}\:\d{1,2}\.\d+? \d{4})\]")
        for lline in self.reverse_readline(log_location):
            # Extract dates from each line
            match = re.match(pattern,lline)
            if match:
                log_date = match.group(1)
                # Convert our date
                log_date = datetime.datetime.strptime(log_date, "%a %b %d %H:%M:%S.%f %Y")
                ftw_start = self.start
                ftw_end = self.end
                # If we have a log date in range
                if log_date <= ftw_end and log_date >= ftw_start:
                    our_logs.append(lline)
                # If our log is from before FTW started stop
                if(log_date < ftw_start):
                    break
        return our_logs

@pytest.fixture
def logchecker_obj():
    return FooLogChecker()
```

Some notes here:
  * The FooLogChecker inherits logcherk.LogChecker so FTW knows it can call the `get_logs()` method
  * We initiate a decorated `@pytest.fixture` so we can pass in a `logchecker_obj` when `test_crs` is called
  * The `test_crs()` method looks similar to most FTW integrations, except it has two extra fixtures: `with_journal` and `tablename`
  * When running `py.test`, pass in `with_journal=/path/to/journal` and `tablename=name` so it can be passed to the testrunner correctly. This will ensure FTW will query the correct journalfile and tablename for the FTW response data
  * Since each stage must be tested and queried, we pass in the `test` fixture and run through each stage with `for stage in test.stages`
  * `runner.run_stage_with_journal` requires the name of the test, the test object, the with_journal path, tablename and the corresponding logchecker_obj

Once you adhere to the new API call for the testrunner, that should be it! FTW will handle querying the sqlite table to get the correct rule-ids, stage-ids and times and return those log lines back to `get_logs()` to test on your log file.
