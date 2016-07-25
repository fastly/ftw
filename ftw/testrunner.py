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

    def test_log(self, lines, log_contains, negate):
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
        if negate:
            assert not found
        else:
            assert found

    def test_response(self, response_object, regex):
        """
        Checks if the response response contains a regex specified in the
        output stage. It will assert that the regex is present.
        """
        if response_object is None:
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

    def run_stage(self, stage, logger_obj=None, http_ua=None):
        """
        Runs a stage in a test by building an httpua object with the stage
        input, waits for output then compares expected vs actual output
        http_ua can be passed in to persist cookies
        """
       
        # Send our request (exceptions caught as needed)
        if stage.output.expect_error:
            with pytest.raises(errors.TestError) as excinfo:
                if not http_ua:
                    http_ua = http.HttpUA()
                start = datetime.datetime.now()
                http_ua.send_request(stage.input)
                end = datetime.datetime.now()
            print '\nExpected Error: %s' % str(excinfo)
        else:
            if not http_ua:
                http_ua = http.HttpUA()
            start = datetime.datetime.now()
            http_ua.send_request(stage.input)
            end = datetime.datetime.now()                
        if (stage.output.log_contains_str or stage.output.no_log_contains_str) \
        and logger_obj is not None:
            logger_obj.set_times(start, end)
            lines = logger_obj.get_logs() 
            if stage.output.log_contains_str:
                self.test_log(lines, stage.output.log_contains_str, False)
            if stage.output.no_log_contains_str:
                # The last argument means that we should negate the resp
                self.test_log(lines, stage.output.no_log_contains_str, True)
        if stage.output.response_contains_str:
            self.test_response(http_ua.response_object,
                               stage.output.response_contains_str)
        if stage.output.status:
            self.test_status(stage.output.status,
                             http_ua.response_object.status)
