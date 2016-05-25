import datetime
import errors
import http
import pytest
import ruleset
import util


class TestRunner(object):
    """
    Runner that accepts stages of a test and verifies expected and actual
    responses
    @TODO
    Accept logger objects for assertions
    """
    def test_status(self, expected_status, actual_status):
        """
        Compares the expected output against actual output of test and stage
        In a separate function to make debugging easy with py.test
        """
        assert expected_status == actual_status
    
    def test_log(self, lines, log_contains):
        """
        Checks if a series of log lines contains a regex specified in the
        output stage. It will flag true on teh first log_contains regex match
        and then assert on the flag at the end of the function
        """
        found = False
        for line in lines:
           if log_contains.search(line):
            found = True
            break
        assert(found)

    def run_stage(self, stage, logger_obj):
        """
        Runs a stage in a test by building an httpua object with the stage
        input, waits for output then compares expected vs actual output
        """
        http_ua = http.HttpUA(stage.input)
        http_ua.send_request()
        self.test_status(stage.output.status, http_ua.response_object.status)

        if stage.output.log_contains:
            start = datetime.datetime.now()
            http_ua.send_request()
            end = datetime.datetime.now()
            logger_obj.set_times(start, end)
            lines = logger_obj.get_logs()
            self.test_log(lines, stage.output.log_contains)
        else:
            http_ua.send_request()
        if stage.output.status:
            self.test_status(stage.output.status,http_ua.response_object.status)
