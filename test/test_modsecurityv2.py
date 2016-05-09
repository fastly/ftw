import pytest
from ftw import testrunner, errors

@pytest.fixture
def modsec_logger_obj():
    """
    Modsec logger object to access in the verifier
    @TODO
    """
    return 0

def test_modsecurityv2(modsec_logger_obj, ruleset, test):
    """
    Modsec specific test
    """
    runner = testrunner.TestRunner() 
    try:
        for stage in test.stages:
            runner.run_stage(stage)
    except errors.TestError as e:
        e.args[1]['meta'] = ruleset.meta
        pytest.fail('Failure! Message -> {0}, Context -> {1}'
                .format(e.args[0],e.args[1]))
    except Exception as e:
        pytest.fail('General failure! Message -> {0}'.format(str(e)))
