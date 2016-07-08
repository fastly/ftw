import pytest
from ftw.ftw import testrunner, errors

def test_default(ruleset, test, destaddr):
    """
    Default tester with no logger obj. Useful for HTML contains and Status code
    Not useful for testing loggers
    """
    runner = testrunner.TestRunner() 
    try:
        for stage in test.stages:
            if destaddr is not None:
                stage.input.dest_addr = destaddr
            runner.run_stage(stage, None)
    except errors.TestError as e:
        e.args[1]['meta'] = ruleset.meta
        pytest.fail('Failure! Message -> {0}, Context -> {1}'
                        .format(e.args[0],e.args[1]))
