from ftw import ruleset, logchecker, testrunner
import pytest
import random
import threading

class LoggerTestObj(logchecker.LogChecker):
    def __init__(self):
        self.do_nothing = False

    def generate_random_logs(self):
        if self.do_nothing:
            return []
        else:
            return [str(self.start) + ' rule-id-' + str(random.randint(10,99))]
        
    def get_logs(self):
        logs = self.generate_random_logs()
        return logs

@pytest.fixture
def logchecker_obj():
    """
    Returns a LoggerTest Integration object
    """
    return LoggerTestObj()

def test_logcontains_withlog(logchecker_obj, ruleset, test):
    runner = testrunner.TestRunner()
    for stage in test.stages:
        runner.run_stage(stage, logchecker_obj)

def test_logcontains_nolog(logchecker_obj, ruleset, test):
    logchecker_obj.do_nothing = True
    runner = testrunner.TestRunner()
    for stage in test.stages:
        runner.run_stage(stage, logchecker_obj)
