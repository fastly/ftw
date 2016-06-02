import datetime
import errors
import http
import pytest
import ruleset
import util
import re


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
        output stage. It will flag true on the first log_contains regex match
        and then assert on the flag at the end of the function
        """
        found = False
        for line in lines:
            if log_contains.search(line):
                found = True
                break
        assert found

    def test_response(self, response_object, regex):
        """
        Checks if the HTML response contains a regex specified in the
        output stage. It will assert that the regex is present.
        """
        if response_object == None:
            raise errors.TestError(
                'Searching before response received',
                {
                    'regex': regex,
                    'response_object': response_object,
                    'function': 'testrunner.TestRunner.test_response'
                })
        if regex.search(response_object.response):                 
            assert True
        else:
            assert False


    def run_stage(self, stage, logger_obj=None):
        """
        Runs a stage in a test by building an httpua object with the stage
        input, waits for output then compares expected vs actual output
        """
        http_ua = http.HttpUA(stage.input)
        if stage.output.log_contains_str and logger_obj is not None:
            start = datetime.datetime.now()
            http_ua.send_request()
            end = datetime.datetime.now()
            logger_obj.set_times(start, end)
            lines = logger_obj.get_logs()
            self.test_log(lines, stage.output.log_contains_str)
        else:
            http_ua.send_request()
        if stage.output.html_contains_str:
            self.test_response(http_ua.response_object, stage.output.html_contains_str)
        if stage.output.status:
            self.test_status(stage.output.status, http_ua.request_object.status)
