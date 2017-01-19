import datetime
from dateutil import parser
import errors
import http
import pytest
import ruleset
import util
import re
import sqlite3

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

    def test_response_str(self, response, regex):
        """
        Checks if the response response contains a regex specified in the
        output stage. It will assert that the regex is present.
        """
        if regex.search(response):
            assert True
        else:
            assert False

    def query_for_stage_results(self, tablename):
        """
        Construct query for sqlite database for a specific stage run from a journal
        Possible SQL injection here, but since its sqlite and if someone had control of the python script
        and the sqlite database, they can just open the database/modify it without using our program
        """
        q = 'SELECT * FROM %s WHERE stage = ? AND test_id = ?' % tablename
        return q

    def run_stage_with_journal(self, rule_id, test, journal_file, tablename, logger_obj):
        """
        Compare entries and responses in a journal file with a logger object
        This will follow similar logic as run_stage, where a logger_obj.get_logs()
        MUST be implemented by the user so times can be retrieved and compared
        against the responses logged in the journal db
        """
        assert logger_obj is not None
        conn = sqlite3.connect(journal_file)
        conn.text_factory = str
        cur = conn.cursor()
        for i, stage in enumerate(test.stages):
            '''
            Query DB here for rule_id & test_title
            Compare against logger_obj
            '''
            q = self.query_for_stage_results(tablename)
            results = cur.execute(q, [i, test.test_title]).fetchall()
            if len(results) == 0:
                raise errors.TestError(
                    'SQL Query did not return results for test',
                    {
                        'rule_id': rule_id,
                        'test': test.test_title,
                        'query': q,
                        'stage_num': i,
                        'function': 'testrunner.TestRunner.run_stage_with_journal'
                    })
            result = results[0]
            start = parser.parse(result[2])
            end = parser.parse(result[3])
            response = result[4]
            status = result[5]
            if (stage.output.log_contains_str or stage.output.no_log_contains_str):
                logger_obj.set_times(start, end)
                lines = logger_obj.get_logs() 
                if stage.output.log_contains_str:
                    self.test_log(lines, stage.output.log_contains_str, False)
                if stage.output.no_log_contains_str:
                    # The last argument means that we should negate the resp
                    self.test_log(lines, stage.output.no_log_contains_str, True)
            if stage.output.response_contains_str:
                self.test_response_str(response,
                                   stage.output.response_contains_str)
            if stage.output.status:
                self.test_status(stage.output.status, status)

    def run_test_build_journal(self, rule_id, test, journal_file, tablename):
        """
        Build journal entries from a test within a specified rule_id
        Pass in the rule_id, test object, and path to journal_file 
        DB MUST already be instantiated from util.instantiate_database()
        """
        conn = sqlite3.connect(journal_file)
        conn.text_factory = str
        cur = conn.cursor()
        for i, stage in enumerate(test.stages):
            response = None
            status = None
            try:
                print 'Running test %s from rule file %s' % (test.test_title, rule_id)
                http_ua = http.HttpUA()
                start = datetime.datetime.now()
                http_ua.send_request(stage.input)
                response = http_ua.response_object.response
                status = http_ua.response_object.status
            except errors.TestError as e:
                print '%s got error. %s' % (test.test_title, str(e))
                response = str(e)
                status = -1
            finally:
                end = datetime.datetime.now()
                ins_q = util.get_insert_statement(tablename)
                cur.execute(ins_q, (rule_id, test.test_title, start, end, response, status, i))
                conn.commit()

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
