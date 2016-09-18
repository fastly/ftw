from ftw import ruleset, testrunner, http, errors
import pytest

def test_default(ruleset, test, destaddr):
    """
    Default tester with no logger obj. Useful for HTML contains and Status code
    Not useful for testing loggers
    """
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
        pytest.fail('Failure! Message -> {0}, Context -> {1}'
                        .format(e.args[0],e.args[1]))
