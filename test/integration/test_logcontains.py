from ftw import ruleset, logchecker, testrunner
import pytest
import random
import threading

class LoggerTestObj(logchecker.LogChecker):
    def generate_random_logs(self):
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

def test_logcontains_integration(logchecker_obj, ruleset, test, http_serv_obj):
    thread = threading.Thread(target = http_serv_obj.serve_forever)
    thread.daemon = True
    thread.start()
    runner = testrunner.TestRunner()
    for stage in test.stages:
        runner.run_stage(stage, logchecker_obj)
    http_serv_obj.shutdown()
